#!/usr/bin/env python3
import os
import sys
import json
import asyncio
import locale
import logging
import requests
import uuid
from collections import deque
from dotenv import load_dotenv
from telethon import TelegramClient, types
from telethon.sessions import StringSession
from telethon.tl.functions.channels import CreateChannelRequest, EditPhotoRequest, EditAdminRequest, LeaveChannelRequest
from telethon.tl.types import ChatAdminRights
from PIL import Image

logging.getLogger('telethon').setLevel(logging.ERROR)
TEMP_DIR = ".temp"
os.makedirs(TEMP_DIR, exist_ok=True)
load_dotenv()

# Configuração de idioma. Defina TG_LANG=PT ou TG_LANG=EN em seu arquivo .env para forçar um idioma.
env_lang = os.getenv('TG_LANG', '').upper()
if env_lang in ['PT', 'EN']:
    LANG = env_lang
else:
    sys_lang = (locale.getdefaultlocale()[0] or '').lower()
    LANG = 'PT' if sys_lang.startswith('pt') else 'EN'

PROGRESS_FILE = os.path.join(TEMP_DIR, 'progress.json')
CLONED_ORIGINALS_FILE = os.path.join(TEMP_DIR, 'originals.json')
CLONES_MADE_FILE = os.path.join(TEMP_DIR, 'clones.json')
THUMBNAIL_URL = "https://i.ibb.co/p58q1JJ/thumbnail.png"
PRE_DOWNLOAD_LIMIT = 5

BANNER = r"""
  ____________   ________    ____  _   ____________ 
 /_  __/ ____/  / ____/ /   / __ \/ | / / ____/ __ \
  / / / / __   / /   / /   / / / /  |/ / __/ / /_/ /
 / / / /_/ /  / /___/ /___/ /_/ / /|  / /___/ _, _/ 
/_/  \____/   \____/_____/\____/_/ |_/_____/_/ |_|  
                                                    
        github.com/DevHuney/tg-cloner
        modded by krov.sh
"""

TRANSLATIONS = {
    'PT': {
        'welcome': "TG Cloner - Iniciando clone!",
        'config_missing': "Configuração inicial:",
        'select_remove': "Digite índices para remover (separados por vírgula) ou ENTER para continuar:",
        'resume': "Retomando canal {}/{} a partir da mensagem {}",
        'progress': "Progresso: {} de {} mensagens",
        'media_download': "Mídia detectada | Baixando...",
        'processing_text': "Processando mensagem de texto...",
        'completed': "\nClone concluído!",
        'error': "Erro: {}",
        'leave_cloned_prompt': "Deseja sair de todos os CANAIS ORIGINAIS que já tiveram o clone concluído?",
        'channels_to_leave': "\nCanais a serem abandonados:",
        'confirm_leave': "\nConfirmar saída de {} canais? (s/n): ",
        'left_channel': "✓ Saiu de: {}",
        'error_leaving': "❌ Erro ao sair de {}: {}",
        'leave_complete': "\nProcesso de saída concluído.",
        'channel_registered': "✓ Canal concluído e registrado: {}",
        'analyze_progress': "Analisando progresso para registrar clones concluídos...",
        'main_menu_prompt': "\nO que você gostaria de fazer?",
        'option_continue': "[1] Continuar clones pendentes",
        'option_leave': "[2] Sair dos canais originais já clonados",
        'option_new_clone': "[1] Iniciar um novo clone",
        'choose_option': "Escolha uma opção: ",
        'invalid_option': "Opção inválida. Saindo.",
    },
    'EN': {
        'welcome': "TG Cloner - Start cloning!",
        'config_missing': "First run setup:",
        'select_remove': "Enter indices to remove (comma-separated) or ENTER to continue:",
        'resume': "Resuming channel {}/{} from message {}",
        'progress': "Progress: {} of {} messages",
        'media_download': "Media detected | Downloading...",
        'processing_text': "Processing text message...",
        'completed': "\nCloning completed!",
        'error': "Error: {}",
        'leave_cloned_prompt': "Do you want to leave all the ORIGINAL CHANNELS that have finished cloning?",
        'channels_to_leave': "\nChannels to be left:",
        'confirm_leave': "\nConfirm leaving {} channels? (y/n): ",
        'left_channel': "✓ Left: {}",
        'error_leaving': "❌ Error leaving {}: {}",
        'leave_complete': "\nLeaving process completed.",
        'channel_registered': "✓ Channel completed and registered: {}",
        'analyze_progress': "Analyzing progress to register completed clones...",
        'main_menu_prompt': "\nWhat would you like to do?",
        'option_continue': "[1] Continue pending clones",
        'option_leave': "[2] Leave already cloned original channels",
        'option_new_clone': "[1] Start a new clone",
        'choose_option': "Choose an option: ",
        'invalid_option': "Invalid option. Exiting.",
    }
}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)

def update_json_file(filepath, key, value):
    data = {}
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                pass
    data[key] = value
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json_file(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def prepare_thumbnail():
    thumb_path = os.path.join(TEMP_DIR, 'thumbnail.jpg')
    try:
        if not os.path.exists(thumb_path):
            r = requests.get(THUMBNAIL_URL, stream=True)
            if r.status_code == 200:
                with open(thumb_path, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
        img = Image.open(thumb_path)
        img.thumbnail((320, 320))
        img.save(thumb_path)
        return thumb_path
    except Exception:
        return None

async def download_media_with_retry(client, message, retries=3):
    for _ in range(retries):
        try:
            fresh = await client.get_messages(message.chat_id, ids=message.id)
            return await client.download_media(fresh, file=TEMP_DIR)
        except Exception:
            await asyncio.sleep(1)
    return None

class MediaQueue:
    def __init__(self, client, msgs):
        self.client = client
        self.queue = deque(m for m in msgs if m.media)
        self.cache = {}

    async def pre_download(self):
        while len(self.cache) < PRE_DOWNLOAD_LIMIT and self.queue:
            m = self.queue.popleft()
            p = await download_media_with_retry(self.client, m)
            if p:
                self.cache[m.id] = p

    async def get_file(self, m):
        return self.cache.pop(m.id) if m.id in self.cache else await download_media_with_retry(self.client, m)
            
async def copy_message(client, src_id, dst_id, msg, mq):
    if msg.action or (not msg.text and not msg.media):
        return None
    print(TRANSLATIONS[LANG]['media_download'] if msg.media else TRANSLATIONS[LANG]['processing_text'])
    
    try:
        if msg.media:
            fp = await mq.get_file(msg)
            thumb, attrs, streaming = None, None, False
            
            if isinstance(msg.media, types.MessageMediaDocument):
                attrs = msg.media.document.attributes
                if any(isinstance(a, types.DocumentAttributeVideo) for a in attrs):
                    streaming = True
                    thumb = prepare_thumbnail()
            
            sent = await client.send_file(
                dst_id, fp,
                caption=msg.raw_text or '',
                formatting_entities=msg.entities,
                thumb=thumb,
                attributes=attrs,
                supports_streaming=streaming
            )
            if fp:
                exists = os.path.exists(fp)
                if exists:
                    try:
                        os.remove(fp)
                    except Exception:
                        pass
            await mq.pre_download()
        else:
            sent = await client.send_message(
                dst_id,
                msg.raw_text or '',
                formatting_entities=msg.entities
            )
        return sent
    except Exception as e:
        print(TRANSLATIONS[LANG]['error'].format(str(e)))
        return None

async def handle_leave_channels(client, cloned_originals_data):
    print(TRANSLATIONS[LANG]['channels_to_leave'])
    channels_to_leave = []
    for channel_id, info in cloned_originals_data.items():
        print(f"- {info.get('name', f'ID: {channel_id}')}")
        channels_to_leave.append((int(channel_id), info.get('name', '')))
    
    confirm = input(TRANSLATIONS[LANG]['confirm_leave'].format(len(channels_to_leave))).lower()
    if confirm in ['s', 'y']:
        for channel_id, name in channels_to_leave:
            try:
                await client(LeaveChannelRequest(channel_id))
                print(TRANSLATIONS[LANG]['left_channel'].format(name))
            except Exception as e:
                print(TRANSLATIONS[LANG]['error_leaving'].format(name, e))
        print(TRANSLATIONS[LANG]['leave_complete'])

async def main():
    clear_screen()
    if not all(os.getenv(k) for k in ['API_ID', 'API_HASH', 'SESSION_STRING']):
        print(TRANSLATIONS[LANG]['config_missing'])
        sys.exit(1)

    client = TelegramClient(
        StringSession(os.getenv('SESSION_STRING')),
        int(os.getenv('API_ID')),
        os.getenv('API_HASH')
    )
    await client.start()

    if (not os.path.exists(CLONED_ORIGINALS_FILE) or not os.path.exists(CLONES_MADE_FILE)) and os.path.exists(PROGRESS_FILE):
        print(TRANSLATIONS[LANG]['analyze_progress'])
        progress_data = load_json_file(PROGRESS_FILE)
        for task in progress_data.get('tasks', []):
            if task.get('clone_id') and task.get('orig_id'):
                try:
                    orig_entity = await asyncio.wait_for(client.get_entity(task['orig_id']), timeout=10.0)
                    messages_info = await asyncio.wait_for(client.get_messages(orig_entity, limit=0), timeout=10.0)
                    total_msgs = messages_info.total

                    if task.get('last_msg', 0) >= total_msgs:
                        clone_entity = await asyncio.wait_for(client.get_entity(types.PeerChannel(task['clone_id'])), timeout=10.0)
                        print(f"Registando clone concluído encontrado no progresso: {orig_entity.title}")
                        update_json_file(CLONED_ORIGINALS_FILE, str(orig_entity.id), {'name': orig_entity.title})
                        update_json_file(CLONES_MADE_FILE, str(clone_entity.id), {'name': clone_entity.title, 'original_id': orig_entity.id})
                except Exception:
                    pass

    cloned_originals_data = load_json_file(CLONED_ORIGINALS_FILE)
    
    # Normaliza os IDs no 'originals.json' para compatibilidade com versões antigas
    temp_normalized_data = {}
    for cid_str, info in cloned_originals_data.items():
        cid_int = int(cid_str)
        # Se o ID for positivo, assume-se que é um ID de canal privado antigo sem o prefixo
        if cid_int > 0:
            # Reconstrói o ID completo que a API do Telegram usa
            normalized_key = str(int(f"-100{cid_int}"))
        else:
            normalized_key = cid_str
        temp_normalized_data[normalized_key] = info
    cloned_originals_data = temp_normalized_data

    progress_data = load_json_file(PROGRESS_FILE)
    has_pending_clones = any(t.get('clone_id') is None or t.get('last_msg', 0) == 0 for t in progress_data.get('tasks', [])) if progress_data else False
    
    user_wants_to_clone = True
    if cloned_originals_data:
        print(TRANSLATIONS[LANG]['main_menu_prompt'])
        if has_pending_clones or os.path.exists(PROGRESS_FILE):
            print(TRANSLATIONS[LANG]['option_continue'])
            print(TRANSLATIONS[LANG]['option_leave'])
            choice = input(TRANSLATIONS[LANG]['choose_option'])
            if choice == '1':
                user_wants_to_clone = True
            elif choice == '2':
                await handle_leave_channels(client, cloned_originals_data)
                user_wants_to_clone = False
            else:
                print(TRANSLATIONS[LANG]['invalid_option'])
                user_wants_to_clone = False
        else:
            print(TRANSLATIONS[LANG]['option_new_clone'])
            print(TRANSLATIONS[LANG]['option_leave'])
            choice = input(TRANSLATIONS[LANG]['choose_option'])
            if choice == '1':
                if os.path.exists(PROGRESS_FILE):
                    os.remove(PROGRESS_FILE)
                user_wants_to_clone = True
            elif choice == '2':
                await handle_leave_channels(client, cloned_originals_data)
                user_wants_to_clone = False
            else:
                print(TRANSLATIONS[LANG]['invalid_option'])
                user_wants_to_clone = False
    
    if not user_wants_to_clone:
        await client.disconnect()
        return

    cloned_original_ids = set(cloned_originals_data.keys())
    dialogs = await client.get_dialogs()
    chans = sorted(
        [d for d in dialogs if (d.is_channel or d.is_group) and '- MNRV' not in d.name and str(d.id) not in cloned_original_ids],
        key=lambda x: x.name.lower()
    )

    if os.path.exists(PROGRESS_FILE):
        data = load_json_file(PROGRESS_FILE)
        data['tasks'] = sorted(data['tasks'], key=lambda x: (x.get('pinned', False), x.get('last_msg', 0)), reverse=True)
    else:
        print(TRANSLATIONS[LANG]['welcome'])
        print("Canais disponíveis para clone:")
        for i, c in enumerate(chans):
            print(f"[{i}] {c.name}")
        rem = input(TRANSLATIONS[LANG]['select_remove'])
        excluded = [chans[int(x)].id for x in rem.split(',')] if rem.strip() else []
        sel = [c for c in chans if c.id not in excluded]
        data = {'tasks': [], 'excluded': excluded}
        for c in sel:
            data['tasks'].append({'orig_id': c.id, 'clone_id': None, 'last_msg': 0, 'pinned': False})
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(data, f)

    for task in data['tasks']:
        orig = task['orig_id']
        try:
            src = await client.get_entity(orig)
        except ValueError:
            print(f"⚠️ Não foi possível encontrar ou acessar o canal com ID {orig}. Pulando.")
            continue
        
        clone = None
        if task.get('clone_id'):
            try:
                clone = await client.get_entity(types.PeerChannel(task['clone_id']))
                expected = f"{src.title} - MNRV"
                if getattr(clone, 'title', None) != expected:
                    clone = None
            except Exception:
                clone = None

        if not clone:
            resp = await client(CreateChannelRequest(title=f"{src.title} - MNRV", about=f"{src.title} by @minervasurvive", broadcast=True))
            clone = resp.chats[0]
            task['clone_id'] = clone.id
            with open(PROGRESS_FILE, 'w') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            if getattr(src, 'photo', None):
                pf = await client.download_profile_photo(src)
                if pf:
                    up = await client.upload_file(pf)
                    try:
                        await client(EditPhotoRequest(channel=clone, photo=up))
                    except:
                        pass
                    os.remove(pf)

            bot = await client.get_entity('@MercuriusLibrarianBot')
            rights = ChatAdminRights(post_messages=True, add_admins=False, invite_users=True, change_info=True, ban_users=True, delete_messages=True, pin_messages=True, edit_messages=True, manage_call=True)
            await client(EditAdminRequest(channel=clone, user_id=bot, admin_rights=rights, rank=''))

        msgs = [m async for m in client.iter_messages(orig, reverse=True)]
        total_msgs = len(msgs)

        if task['last_msg'] >= total_msgs:
            print(TRANSLATIONS[LANG]['channel_registered'].format(src.title))
            update_json_file(CLONED_ORIGINALS_FILE, str(src.id), {'name': src.title})
            update_json_file(CLONES_MADE_FILE, str(clone.id), {'name': clone.title, 'original_id': src.id})
            continue

        mq = MediaQueue(client, msgs)
        await mq.pre_download()

        if not task['pinned']:
            for idx, m0 in enumerate(msgs):
                if not m0.action and m0.text:
                    sent0 = await copy_message(client, orig, clone.id, m0, mq)
                    if sent0:
                        try:
                            await client.pin_message(clone, sent0, notify=False)
                        except:
                            pass
                        task['pinned'] = True
                        task['last_msg'] = idx + 1
                        with open(PROGRESS_FILE, 'w') as f:
                            json.dump(data, f)
                        break

        start_idx = task['last_msg']
        for idx in range(start_idx, total_msgs):
            print(TRANSLATIONS[LANG]['progress'].format(idx + 1, total_msgs))
            await copy_message(client, orig, clone.id, msgs[idx], mq)
            task['last_msg'] = idx + 1
            with open(PROGRESS_FILE, 'w') as f:
                json.dump(data, f)

        fixed = str(uuid.uuid4())
        formatted_channel_id = int(f"-100{clone.id}")
        message_data = {"name": src.title, "channel_id": formatted_channel_id, "fixed_uuid": fixed, "link": ""}
        await client.send_message('me', json.dumps(message_data, ensure_ascii=False, indent=4))
        await client.send_message('me', f"Link -> https://cursos.mnrv.lat/{fixed}")

        print(TRANSLATIONS[LANG]['channel_registered'].format(src.title))
        update_json_file(CLONED_ORIGINALS_FILE, str(src.id), {'name': src.title})
        update_json_file(CLONES_MADE_FILE, str(clone.id), {'name': clone.title, 'original_id': src.id})

    print(TRANSLATIONS[LANG]['completed'])

if __name__ == '__main__':
    asyncio.run(main())

