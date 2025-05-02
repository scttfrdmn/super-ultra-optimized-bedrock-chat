#!/usr/bin/env python3
import json,os,boto3,typer
from rich import console,live,markdown,table
from .__version__ import __version__
app,con=typer.Typer(rich_markup_mode="rich"),console.Console(highlight=False)
@app.callback(invoke_without_command=True)
def main(v:bool=typer.Option(False,"--version","-v"),p:str=typer.Option(None,"--profile"),r:str=typer.Option("us-east-1","--region"),c:typer.Context=typer.Context):
    if v:con.print(f"v{__version__}");raise typer.Exit()
    globals().update({"p":p,"r":r});c.invoked_subcommand or chat()
@app.command()
def list_provisioned():
    """List active provisioned throughput commitments (hourly billing)"""
    p=globals().get("p");r=globals().get("r","us-east-1")
    con.print(f"[bold cyan]Checking for provisioned throughput commitments in {r}...[/bold cyan]")
    s=boto3.Session(profile_name=p);bd=s.client("bedrock",region_name=r)
    try:
        t=table.Table(title=f"[bold yellow]Provisioned Throughput Commitments[/bold yellow]", border_style="red")
        [t.add_column(c,style=s) for c,s in [("Model","cyan"),("Name","green"),("Commitment","yellow"),("Created","dim")]]
        throughputs = bd.list_provisioned_model_throughputs().get("provisionedModelSummaries", [])
        if throughputs:
            for tp in throughputs:
                t.add_row(
                    tp.get("modelId","Unknown"),
                    tp.get("provisionedModelName","Unknown"),
                    tp.get("commitmentDuration","Unknown"),
                    tp.get("creationTime","Unknown").strftime("%Y-%m-%d") if hasattr(tp.get("creationTime"), "strftime") else str(tp.get("creationTime","Unknown"))
                )
            con.print(t)
            con.print("[bold red]Warning:[/bold red] These provisioned throughput commitments incur hourly charges until explicitly deleted in AWS console")
        else:
            con.print("[green]No active provisioned throughput commitments found.[/green]")
    except Exception as e:
        con.print(f"[bold red]Error:[/bold red] {e}")

@app.command()
def list_models():
    """List all available models"""
    p=globals().get("p");r=globals().get("r","us-east-1")
    con.print(f"Checking region {r}...")
    s=boto3.Session(profile_name=p)
    bd=s.client("bedrock",region_name=r)
    # Foundation models
    try:
        models = bd.list_foundation_models().get("modelSummaries",[])
        con.print(f"[bold cyan]Foundation models:[/bold cyan] {len(models)}")
        for m in models:
            if "TEXT" in [mode.upper() for mode in m.get("outputModalities",[])]:
                model_id = m["modelId"]
                if "claude" in model_id:
                    con.print(f"Found Claude model: {model_id}")
    except Exception as e:
        con.print(f"[bold red]Error checking foundation models:[/bold red] {e}")
    
    # Inference profiles
    try:
        profiles = bd.list_inference_profiles().get("inferenceProfileSummaries",[])
        con.print(f"[bold cyan]Inference profiles:[/bold cyan] {len(profiles)}")
        for p in profiles:
            if "claude" in p.get("inferenceProfileId",""):
                model_type = ""
                if any(prov_term in p.get('inferenceProfileId',"").lower() for prov_term in ["provisioned", "throughput"]) or "claude-3-7" in p.get('inferenceProfileId',"").lower():
                    model_type = " [bold red](Provisioned throughput - hourly charges apply)[/bold red]"
                con.print(f"Found Claude profile: {p.get('inferenceProfileName')} - {p.get('inferenceProfileId')}{model_type}")
    except Exception as e:
        con.print(f"[bold red]Error checking inference profiles:[/bold red] {e}")
    
    # Check provisioned throughput (active commitments)
    try:
        con.print(f"[bold cyan]Checking provisioned throughput commitments:[/bold cyan]")
        throughputs = bd.list_provisioned_model_throughputs().get("provisionedModelSummaries", [])
        if throughputs:
            for t in throughputs:
                con.print(f"[bold yellow]Active commitment:[/bold yellow] {t.get('modelId')} - {t.get('provisionedModelName')} - {t.get('commitmentDuration')}")
        else:
            con.print("No active provisioned throughput commitments found.")
    except Exception as e:
        con.print(f"[bold red]Error checking provisioned throughput:[/bold red] {e}")
@app.command()
def chat(clear:bool=False,all:bool=False):
    if clear:os.system("cls" if os.name=="nt" else "clear")
    s=boto3.Session(profile_name=globals().get("p"));r=globals().get("r","us-east-1")
    rt,bd,ms,en=s.client("bedrock-runtime",region_name=r),s.client("bedrock",region_name=r),{},set()
    test=lambda m:json.dumps({"anthropic_version":"bedrock-2023-05-31","max_tokens":1,"messages":[{"role":"user","content":[{"type":"text","text":"."}]}]} if "anthropic" in m else {"inputText":".","textGenerationConfig":{"maxTokenCount":1}})
    with con.status("[cyan]Discovering models...[/cyan]"):
        # Get foundation models
        for m in bd.list_foundation_models().get("modelSummaries",[]):
            if "TEXT" in [mode.upper() for mode in m.get("outputModalities",[])]:a=m["modelId"].split(".")[-1].split("-v")[0];ms[a]=m["modelId"]
            try:rt.invoke_model(modelId=m["modelId"],body=test(m["modelId"]));en.add(a)
            except:pass
        
        # Get inference profiles from user's configured region
        try:
            for prof in bd.list_inference_profiles().get("inferenceProfileSummaries",[]):
                # Handle inference profiles correctly
                prof_id = prof["inferenceProfileId"]
                name = prof_id.split(".")[-1] # Get the base name without the "us." prefix
                ms[name]=prof_id
                try:rt.invoke_model(modelId=prof_id,body=test(prof_id));en.add(name)
                except:pass
        except:pass
    
    t=table.Table(title=f"[bold cyan]Ultra Bedrock Chat v{__version__}[/bold cyan]", border_style="blue")
    [t.add_column(c,style=s) for c,s in [("Model","cyan"),("Type","yellow"),("ID","green")]]
    for a,i in sorted(ms.items(),key=lambda x:(x[0] not in en,x[0])):
        if all or a in en:
            # Determine model type
            model_type = "On-Demand"
            if i.startswith("us."):
                # Check if it's a provisioned throughput model
                if any(prov_term in i.lower() for prov_term in ["provisioned", "throughput"]) or "claude-3-7" in i.lower():
                    model_type = "[bold red]Provisioned $[/bold red]"
                else:
                    model_type = "Inference Profile"
            t.add_row(a, model_type, i[:40]+"..." if len(i)>40 else i)
    con.print(t);hist=[];inp=typer.prompt("Model")
    if inp.lower() == "exit":return
    model=inp if inp.startswith(("arn:","us.")) else ms.get(inp)
    if not model:con.print("[bold red]Model not found![/bold red]");return
    # Warn about provisioned throughput costs
    if any(prov_term in model.lower() for prov_term in ["provisioned", "throughput"]) or "claude-3-7" in model.lower():
        con.print("[bold red]Warning:[/bold red] This model uses provisioned throughput which incurs hourly costs until explicitly deleted in AWS console")
    while (msg:=typer.prompt("",prompt_suffix="You: "))!="exit":
        if msg=="clear":hist=[];con.print("[italic green]History cleared[/italic green]");continue
        try:
            ic,txt="anthropic" in model,""
            body=json.dumps({"anthropic_version":"bedrock-2023-05-31","max_tokens":1024,"messages":hist+[{"role":"user","content":[{"type":"text","text":msg}]}]} if ic else {"inputText":msg,"textGenerationConfig":{"maxTokenCount":512}})
            with live.Live(markdown.Markdown("")) as l:
                for chunk in rt.invoke_model_with_response_stream(modelId=model,body=body).get("body"):
                    if "chunk" in chunk:d=json.loads(chunk["chunk"]["bytes"]);txt+=(d.get("delta",{}).get("text","") if "delta" in d else "".join([b.get("text","") for b in d.get("content",[]) if b.get("type")=="text"])) if ic else d.get("completion","");l.update(markdown.Markdown(txt))
            hist+=[{"role":"user","content":[{"type":"text","text":msg}]},{"role":"assistant","content":[{"type":"text","text":txt}]}] if txt.strip() else []
        except Exception as e:con.print(f"[bold red]Error:[/bold red] {e}")
if __name__=="__main__":app()