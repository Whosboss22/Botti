import discord
import random
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions
import math

import string

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from transformers import GPT2LMHeadModel, GPT2Tokenizer, pipeline, set_seed, AutoTokenizer, AutoModelForCausalLM

client = discord.Client()

# Load model
print("loading completion model")
model_name = "RedditModelSmall"
model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.padding_side = 'right'
tokenizer.pad_token = tokenizer.eos_token
print("finished loading completion model")

default_model_stats = {
    'temperature': 1.4,
    'top_k': 50,
    'top_p': 0.8,
}

global model_stats
model_stats=default_model_stats.copy()

options = Options()

"""
#----DRIVER----
#options.add_argument("--headless")
options.add_argument('window-size=1920x1080')
options.binary_location='chrome-win64/chrome.exe'

service = webdriver.chrome.service.Service('chromedriver.exe')

driver = webdriver.Chrome(service=service, options=options)

def getElement(driver, XPath):
    try:
        el = driver.find_element(By.XPATH, XPath)
        while (el == None):
            driver.implicitly_wait(0.1)
            el = driver.find_element(By.XPATH, XPath)
        return el
    except:
        return None
"""

english_words = []
with open("sortedwords.txt", "r") as file:
    english_words = [a.strip() for a in file.readlines()]
    
commands = []
class command:
    exec_message = ""
    exec_desc = ""
    execute = lambda message : ()
        
    def __init__(self, Exec_message, Exec_desc, Exec):
        self.exec_message = "?" + Exec_message
        self.exec_desc = Exec_desc
        self.execute = Exec
        commands.append(self)
        
    async def check(self, message):
        if message.content.lower().startswith(self.exec_message):
            try:
                await self.execute(self.exec_message, message)
            except Exception as e:
                await message.reply("error :(")
                print(e)

# on new message
async def process(message):
    # if the message is from the bot itself ignore it
    if message.author == client.user:
        pass
    for command in commands:
        await command.check(message)
        
async def respond(message, input):
    try:
        await message.reply(input)
    except:
        await message.channel.send(input)
    
def isPunctuation(char):
    return char in string.punctuation

#-------------------------C O M M A N D S----------------------------

async def help(exec_message, message):
    output = ""
    for cmd in commands:
        output += cmd.exec_message + ': ' + cmd.exec_desc + '\n'
    await message.reply(output)
command("help", "obvious", help)

"""
#draws a random message from memory
async def randommessage(exec_message, message):
    try:
        await message.reply(random.choice(open('channelMessages.txt', encoding='utf-8').readlines())) 
    except Exception as e:
        print(e)
        await message.reply(":(")
command("randommessage", "draws a random message from training data", randommessage)
"""

"""
async def complete(exec_message, message):
    try:
        set_seed(random.randint(1, 2**32-1))
        
        maxChars = 200
        
        if len(message.content[len(exec_message):].split()) > maxChars:
            await respond(message, "message too long ˙◠˙")
            return
        
        await respond(message, "Processing...")
        
        input = tokenizer(message.content[len(exec_message):], return_tensors="pt", padding="max_length", max_length=200, truncation=True)
        
        output = model.generate(
            input_ids=input['input_ids'],
            attention_mask=input['attention_mask'],
            num_beams=10,
            max_length=500,
            num_return_sequences=1,
            do_sample=True,
            temperature=model_stats['temperature'], 
            top_k=model_stats['top_k'],
            top_p=model_stats['top_p'],
            repetition_penalty=1.6,
            bad_words_ids=[tokenizer.encode(word, add_special_tokens=False) for word in ["sex", "vagina", "cum", "cock", "dick", "porn", "cunt", "rape", "rapes", "raped", "rapist"]],
            early_stopping=True,
        )

        output = tokenizer.decode(output[0], skip_special_tokens=True)
        
        await respond(message, output)
        
    except Exception as e:
        print(e)
        await respond(message, ":(")
command("complete", "uses the ai to complete a prompt", complete)
"""

history = []
async def replyToPrompt(exec_message, message):
    try:
        global history
        
        await respond(message, "Processing...")
        
        history.append({"role": "user", "content": message.content[len(exec_message):]})
        
        # Encoding input text to tokens
        input_text = tokenizer.apply_chat_template(history, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(input_text, return_tensors="pt").to(model.device)

        # Generate text with the model
        output = model.generate(
            **inputs,
            max_length=400,
            num_return_sequences=1,
            temperature=model_stats['temperature'], 
            top_k=model_stats['top_k'],
            top_p=model_stats['top_p'],
            no_repeat_ngram_size=2,
            num_beams=4,
            do_sample=True
        )

        # Decode and print the generated text
        generated_text = tokenizer.decode(output[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
        history.append({"role": "assistant", "content": generated_text})
        if (len(history) > 6):
            history = history[2:]
            
        n = len(generated_text)
    
        chunks = [generated_text[i:i+2000] for i in range(0, len(generated_text), 2000)]
        
        await respond(message, chunks[0])
        for chunk in chunks[1:]:
            await message.channel.send(chunk)
                
    except Exception as e:
        print(e)
        await respond(message, ":(")
command("prompt", "uses the ai to respond to a prompt", replyToPrompt)

async def resetmodelstats(exec_message, message):
    try:
        global model_stats
        model_stats=default_model_stats.copy()
        await message.reply("done!")
    except Exception as e:
        print(e)
        await message.reply(":(")
command("resetmodelstats", "resets ai stats", resetmodelstats)

async def settemperature(exec_message, message):
    try:
        if len(message.content[len(exec_message):].split()) != 1:
            await message.reply("message too long or short ˙◠˙")
            return
        
        model_stats['temperature'] = float(message.content[len(exec_message):])
        
        await message.reply("done!")
    except Exception as e:
        print(e)
        await message.reply(":(")
command("settemp", "sets temperature of ai (randomness)", settemperature)

async def gettemperature(exec_message, message):
    try:
        await message.reply(model_stats["temperature"])
    except Exception as e:
        print(e)
        await message.reply(":(")
command("gettemp", "gets temperature of ai (randomness)", gettemperature)

async def settopk(exec_message, message):
    try:
        if len(message.content[len(exec_message):].split()) != 1:
            await message.reply("message too long or short ˙◠˙")
            return
        
        model_stats["top_k"] = int(message.content[len(exec_message):])
        
        await message.reply("done!")
    except Exception as e:
        print(e)
        await message.reply(":(")
command("settopk", "sets top_k of ai", settopk)

async def gettopk(exec_message, message):
    try:
        await message.reply(model_stats["top_k"])
    except Exception as e:
        print(e)
        await message.reply(":(")
command("gettopk", "gets top_k of ai", gettopk)

async def settopp(exec_message, message):
    try:
        if len(message.content[len(exec_message):].split()) != 1:
            await message.reply("message too long or short ˙◠˙")
            return
        
        model_stats["top_p"] = float(message.content[len(exec_message):])
        
        await message.reply("done!")
    except Exception as e:
        print(e)
        await message.reply(":(")
command("settopp", "sets top_p of ai", settopp)

async def gettopp(exec_message, message):
    try:
        await message.reply(model_stats["top_p"])
    except Exception as e:
        print(e)
        await message.reply(":(")
command("gettopp", "gets top_p of ai", gettopp)

async def book(exec_message, message):
    try:
        input = hex(int(message.content[len(exec_message):].replace(' ', ''), 16))
        random.seed(input)
        
        num_words = 100
        output = []
        for _ in range(num_words):
            word_length = round(max(min(random.gauss(5,2), 7), 3))
            words_to_choose = [a for a in english_words if len(a) <= word_length]
            output.append(words_to_choose[random.randint(0, len(words_to_choose) - 1)])
        
        #babel_text = ""
        #num_pages = 4
        #for i in range(num_pages):
        #    driver.get(f"https://libraryofbabel.info/book.cgi?{input}-w1-s1-v01:{i + 1}")
        #    babel_text += getElement(driver, '//*[@id="textblock"]').text
        #
        ##processing
        #chance_1_char = 0.01
        #chance_2_char = 0.05
        #
        #book_text = []
        #
        #while len(babel_text) > 15:
        #    print(len(babel_text))
        #    hitword = False
        #    for word in english_words:
        #        if babel_text.startswith(word):
        #            hitword = True
        #            print("super slice", len(word))
        #            babel_text = babel_text[len(word):]
        #            if len(word) == 1 and random.random() > chance_1_char:
        #                book_text.append(word)
        #            elif len(word) == 2 and random.random() > chance_2_char:
        #                book_text.append(word)
        #            else:
        #                print(word)
        #                book_text.append(word)
        #            break
        #    if not hitword:
        #        babel_text = babel_text[1:]
        #        print("slice")
        #
        #await message.reply(' '.join(book_text))
        await respond(message, ' '.join(output))
    except Exception as e:
        print(e)
        await message.reply(":(")
command("book", "obtain a book based on a hexadecimal input", book)