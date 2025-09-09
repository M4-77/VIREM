from ollama import generate # the actual ai servers n stuff, sudo pacman -S ollama then pull a model from the list, i recommend either illama3.2 or gpt-oss, use a 20b parameter model or less as the higher the parameter the longer the response time unless u have an insane pc
import subprocess,platform,psutil,shutil,os,random,re # processes for tasks anbd reading the operating system, random is currently unused but will be implemented later
from datetime import datetime,timedelta # so virem can note the time, but I haven't actually implemented the time into the knowledge ¯\_(ツ)_/¯

# as of 9/9/25 there isn't any voice recognition or ability to talk to it yet, having some trouble with that side of things

def get_system_specs():
    s={}
    s["OS"]=platform.system()+" "+platform.release()
    s["OS Version"]=platform.version()
    try:
        cpu_name=platform.processor()
        if not cpu_name:
            with open("/proc/cpuinfo") as f:
                for l in f:
                    if "model name" in l: cpu_name=l.strip().split(":")[1].strip(); break   # linux exclusive im pretty sure so if someone can port this to windows that would be great
        s["CPU"]=cpu_name
    except: s["CPU"]="Unknown"
    s["Cores"]=psutil.cpu_count(logical=False)
    s["Threads"]=psutil.cpu_count(logical=True)
    r=psutil.virtual_memory()
    s["Total RAM (GB)"]=round(r.total/1e9,2)
    d=shutil.disk_usage("/")
    s["Total Disk (GB)"]=round(d.total/1e9,2)
    s["Used Disk (GB)"]=round(d.used/1e9,2)
    s["Free Disk (GB)"]=round(d.free/1e9,2)
    return s

#directories
DOCUMENTS_DIR=os.path.expanduser("~/Documents")
DOWNLOADS_DIR=os.path.expanduser("~/Downloads")
NOTES_DIR=os.path.join(DOCUMENTS_DIR,"notes")

#tool functions
def create_project(name,directory=DOCUMENTS_DIR):
    p=os.path.join(directory,name)
    try: os.makedirs(p,exist_ok=True);  return f"Project '{name}' created at {p}"
    except Exception as e: return f"Error creating project: {e}"
def delete_file(path):
    if not os.path.exists(path): return f"File {path} does not exist."
    os.remove(path); return f"Deleted {path}"
def write_note(text):
    n=datetime.now()
    df=os.path.join(NOTES_DIR,n.strftime("%Y-%m-%d"))
    os.makedirs(df,exist_ok=True)
    hour_str=n.strftime("%I%p").lstrip("0").lower()
    np=os.path.join(df,f"{hour_str}.txt")
    with open(np,"a",encoding="utf-8") as f: f.write(text+"\n")
    return f"Added to note: {np}"
def clear_downloads():
    now,week_ago,removed=datetime.now(),datetime.now()-timedelta(days=7),[]
    try:
        for f in os.listdir(DOWNLOADS_DIR):
            fp=os.path.join(DOWNLOADS_DIR,f)
            if os.path.isfile(fp):
                try: mtime=datetime.fromtimestamp(os.path.getmtime(fp))
                except: mtime=None
                if mtime is None or mtime<week_ago: os.remove(fp); removed.append(f)
        return f"Removed files: {removed}" if removed else "No files to remove."
    except Exception as e: return f"Error clearing downloads: {e}"
def open_application(app):
    try: subprocess.Popen([app]); return f"Launched application: {app}"
    except Exception as e: return f"Error launching {app}: {e}"
def calculator(expr):
    try: return f"Result: {eval(expr,{'__builtins__':{}})}"
    except Exception as e: return f"Calc error: {e}"
def handle_tool_command(cmd):
    if cmd.startswith("open:"): return open_application(cmd.split("open:",1)[1].strip())
    elif cmd.startswith("clear_downloads"): return clear_downloads()
    elif cmd.startswith("note:"): return write_note(cmd.split("note:",1)[1].strip())
    elif cmd.startswith("create_project:"): return create_project(cmd.split("create_project:",1)[1].strip())
    elif cmd.startswith("delete:"): return delete_file(os.path.join(DOCUMENTS_DIR,cmd.split("delete:",1)[1].strip()))
    elif cmd.startswith("calc:"): return calculator(cmd.split("calc:",1)[1].strip())
    return f"Unknown tool command: {cmd}"
with open("personality-core.txt","r",encoding="utf-8") as f: personality_prompt=f.read()

# config, i should prob put this either at the top or in a seperate file
Hostility,Boredom,Corruption=1,5,0 # as of 9/9/25 not implemented but it'll get the responses to act accordingly to the emotion
Rage=(Hostility/2)*Corruption/1.5 # random calculation i made up to increase its rage
message_history=[];MAX_HISTORY=10 # max message history, this increases prompt size and therefore number of tokens so keep this moderately low as it'll increase response time drastically if you have longer answers


print("VIREM is activated. Type the word exit to quit.\n")

while True:
    user_input=input("You: ")
    if user_input.lower() in ("exit","quit"): break
    message_history.append({"role":"user","content":user_input})
    if len(message_history)>MAX_HISTORY: message_history=message_history[-MAX_HISTORY:] # removes any history above the max history
    specs=get_system_specs()
    specs_text="System Specs:\n"+"\n".join([f"{k}: {v}" for k,v in specs.items()]) # joins specs to the prompt
    full_prompt=personality_prompt+"\n\n"+specs_text+"\n"
    for msg in message_history: full_prompt+=f"{msg['role'].capitalize()}: {msg['content']}\n"
    full_prompt+="VIREM: " # you can change the name of VIREM if you wanted to here but why would you do that lmao
    response=generate("gpt-oss:20b",full_prompt)       #<------------------------------------------------------------    the AI model you pull should be put here, i'll add it to config once i set that up
    assistant_text=response['response']
    tools=re.findall(r"<tool>(.*?)</tool>",assistant_text,re.DOTALL)
    for t in tools: print(f"[VIRE-Tool]: {handle_tool_command(t)}")
    clean_text=re.sub(r"<tool>.*?</tool>","",assistant_text).strip()
    print(f"VIREM: {clean_text}")
    if clean_text: subprocess.run(["espeak",clean_text]) # uses espeak to output, sudo pacman -S espeak in terminal if you haven't already as it's pretty cool
    message_history.append({"role":"assistant","content":assistant_text})
    if len(message_history)>MAX_HISTORY: message_history=message_history[-MAX_HISTORY:]
