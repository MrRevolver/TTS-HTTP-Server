import os
import torch
import re
import sys
import yaml
from transliterate import translit
from pathlib import Path
from num2text import num2text

torch.set_grad_enabled(False)
device = torch.device('cpu')
torch.set_num_threads(4) 

FILE_V3 = 'v3_1_ru.pt'

DIR_CACH = 'cach'
if not os.path.isdir(DIR_CACH):
    os.mkdir(DIR_CACH)
    
FILE_OPT  = os.path.join('options', 'options.yml')

with open(FILE_OPT, 'r', encoding="utf-8") as y:   
    OPTIONS = yaml.safe_load(y)

DEFAULT = OPTIONS['tts']
PARAMS  = OPTIONS['params']

SAMPLE_RATE = DEFAULT.get('sample_rate', 48000)
SPEAKER_V3 = DEFAULT.get('speaker', 'xenia')

# Экраинируем невоспроизводимые символы 
def fecran(txt):
    for i in '[]{}|':
        txt = txt.replace(i, f'\\{i}')
    return txt 

# Транслитерация
def ftrans(txt):
    return translit(txt, 'ru')

# Меняем цифры на числительные
def fnum(txt):
    x = re.findall('[0-9]+', str(txt))
    x.sort(reverse=True)
    for i in x:
        txt = str(txt).replace(i, num2text(int(i)))
    return txt

# Обработка аббревиатуры
def fabr(txt):
    for abr in re.findall('[А-ЯЁ]{2,}', txt):
        aabara = ''
        for i,a in enumerate(abr):
            if a in 'АЕЁИОУЫЭЮЯ':
                aabara += a+a.lower()
            elif a in 'КХШЩ':
                aabara += a+'а+а'
            elif a in 'ЛМНРСФ':
                aabara += 'ээ'+ a
            elif a in 'БВГДЖЗПТЦЧ':
                aabara += a+'ээ'
            elif a == 'Й': aabara += 'ё'
            aabara = aabara.replace('ээээ', 'эээ')
        txt = txt.replace(abr, f'<prosody rate="fast"> {aabara} </prosody>')
    return txt

def fix(txt, *, num=True, trans=True, abr=True):
    if isinstance(txt, str):
        txt = fecran(txt)
        if trans: txt = ftrans(txt)
        if abr:   txt = fabr(txt)
    if num: txt = fnum(txt)
    return txt
           
class V3:

    def __init__(self):
        self.model = torch.package.PackageImporter(FILE_V3).load_pickle("tts_models", "model")
        self.model.to(device)
        self.delete = []
        
    # Получить название голоса
    def get_name(self, speaker=None):
        name = SPEAKER_V3 if self.speakers().count(SPEAKER_V3) else self.speakers()[0]
        if speaker is None: return name
        if str(speaker).isdigit(): speaker = int(speaker)
        if type(speaker) == int:
            if speaker - 1 < len(self.speakers()): 
                return sorted(self.speakers())[speaker - 1]
        if type(speaker) == str and self.speakers().count(speaker): return speaker
        return None
    
    # Список голосов
    def speakers(self):
        return sorted(self.model.speakers)
    
    def get_size_cach(self):
        return sum(os.path.getsize(DIR_CACH+os.sep+f) for f in os.listdir(DIR_CACH) if os.path.isfile(DIR_CACH+os.sep+f))
    
    def rotate(self):
        size_cach = self.get_size_cach()
        mb = size_cach/1024/1024
        self.delete = []
        if mb > PARAMS.get('size_cach', 2):
            max_size = PARAMS.get('size_cach')*1024*1024
            li = {}
            for a in os.listdir(DIR_CACH):
                m = os.path.getmtime(DIR_CACH+os.sep+a)
                s = os.path.getsize(DIR_CACH+os.sep+a)
                f = DIR_CACH+os.sep+a
                li[f] = (m, s)
           
            li = sorted(li.items(), key=lambda x: x[1][0], reverse=True)
            
            for f, (m, s) in li:
               max_size -= s
               if max_size < 0:
                self.delete.append(f)
                os.remove(f)
            
    def __call__(self, text, path=None, 
                speaker=SPEAKER_V3, 
                sample_rate=SAMPLE_RATE, 
                ssml=False,
                accent=False, 
                yo=False, 
                abr=True,
                rw=False):
        print('Входящий текст:', text)
        bname = re.sub('[^\w_\. ]', '_', str(text))[:100]
        fspeaker = self.get_name(speaker)
        fname = os.path.join(DIR_CACH, f'{fspeaker}_{bname}.wav') if path is None else path
        print('Кэш:', fname)
        if os.path.isfile(fname):
            if rw: 
                os.remove(fname)
            else:
                Path(fname).touch()
                return fname
        
        if (ssml):
            #ssml  = '<speak>%s</speak>' % fix(text)
            print('Синтез SSML:', fix(text))
            self.model.save_wav(ssml_text=fix(text),
                                speaker=fspeaker,
                                sample_rate=sample_rate,
                                audio_path=fname,
                                put_accent=accent,
                                put_yo=yo)
        else:
            print('Синтез Text:', fix(text))
            self.model.save_wav(text=fix(text),
                                speaker=fspeaker,
                                sample_rate=sample_rate,
                                audio_path=fname,
                                put_accent=accent,
                                put_yo=yo)
        self.rotate() 
        return fname               