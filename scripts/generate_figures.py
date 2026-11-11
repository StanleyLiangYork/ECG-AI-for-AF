"""Reproduce review figures from aggregate CSVs, with no raw-data access."""
from pathlib import Path
import argparse, csv, math, subprocess, sys, textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
def read(name):
    with (ROOT/'data'/name).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def wilson(n,N):
    n,N=float(n),float(N)
    if not (N>0 and 0<=n<=N):raise ValueError('Invalid binomial count')
    z=1.959963984540054;p=n/N;q=1+z*z/N
    m=(p+z*z/(2*N))/q;h=z*math.sqrt(p*(1-p)/N+z*z/(4*N*N))/q
    return (0.0 if n==0 else m-h),(1.0 if n==N else m+h)
def save(fig,name,args):
    for ext in ('png','pdf','svg'):
        fig.savefig(args.output/f'{name}.{ext}',dpi=args.dpi,bbox_inches='tight',facecolor='white',transparent=False)
    plt.close(fig)
def box(ax,x,y,w,h,text,fill='white',size=10):
    ax.add_patch(Rectangle((x,y),w,h,facecolor=fill,edgecolor='#333333',lw=1))
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=size)
def arrow(ax,start,end):ax.add_patch(FancyArrowPatch(start,end,arrowstyle='-|>',mutation_scale=12,color='#333333'))
def framework(args):
    rows=read('framework.csv');panels=list(dict.fromkeys(r['panel'] for r in rows))
    fig,ax=plt.subplots(figsize=(12,8));ax.set(xlim=(0,12),ylim=(0,9));ax.axis('off')
    for j,panel in enumerate(panels):
        y=6.4-j*2.7;rs=[r for r in rows if r['panel']==panel];w=11.4/len(rs)
        ax.text(.3,y+2.15,panel,weight='bold',size=13,color='#12396a')
        for k,r in enumerate(rs):
            x=.3+k*w
            text=r['heading']+'\n\n'+textwrap.fill(r['detail'],24 if len(rs)==4 else 32)
            box(ax,x,y,w-.14,1.95,text,'#f2f6fa',9.5)
        if j<2:ax.text(6,y-.3,'Define population, clinical outcome, time horizon, and analysis unit.' if j==0 else 'Check knowledge provenance, information timing, data leakage, and reproducibility.',ha='center',fontsize=10)
    ax.text(6,-.4,'Bias and applicability are distinct. Benchmark accuracy does not establish clinical benefit.',ha='center',fontsize=10)
    save(fig,'figure1_clinical_framework',args)
def prisma(args):
    c={r['key']:int(r['count']) for r in read('prisma.csv')}
    assert c['records']-c['duplicates']==c['screened']
    assert c['screened']-c['excluded_screening']==c['assessed']
    assert c['assessed']-c['excluded_full_text']==c['included']
    fig,ax=plt.subplots(figsize=(10,10));ax.set(xlim=(0,10),ylim=(0,11));ax.axis('off')
    box(ax,.7,10,8.9,.6,'Identification of studies via databases and registers','#f7c545',12)
    stages=[(8.1,1.5,f"Records identified from databases (n={c['records']})\nPubMed {c['pubmed']}; Web of Science {c['wos']}\nIEEE Xplore {c['ieee']}; CDSR {c['cdsr']}; CENTRAL {c['central']}"),(6.5,.8,f"Records screened (n={c['screened']})"),(4.8,.9,f"Reports sought for retrieval (n={c['assessed']})"),(2.8,1,f"Reports assessed for eligibility (n={c['assessed']})"),(.8,.9,f"Studies included in review (n={c['included']})\nReports included (n={c['included']})")]
    for i,(y,h,t) in enumerate(stages):
        box(ax,1,y,4.1,h,t,size=10)
        if i:arrow(ax,(3.05,stages[i-1][0]),(3.05,y+h))
    for y,h,t in [(8.1,1.5,f"Records removed before screening\nDuplicates (n={c['duplicates']})\nAutomation exclusions (n=0)\nOther removals (n=0)"),(6.5,.8,f"Records excluded (n={c['excluded_screening']})"),(4.8,.9,f"Reports not retrieved (n={c['unretrieved']})"),(2.3,1.7,f"Reports excluded (n={c['excluded_full_text']})\nPublication/design (n={c['publication_type']})\nAI component (n={c['component']})\nAF task/result (n={c['af_result']})\nAdult population (n={c['population']})\nECG input (n={c['ecg_input']})")]:
        box(ax,5.8,y,3.8,h,t,size=10);arrow(ax,(5.1,y+h/2),(5.8,y+h/2))
    ax.text(.3,8.8,'Identification',rotation=90,ha='center',va='center',fontsize=11)
    ax.text(.3,4.8,'Screening',rotation=90,ha='center',va='center',fontsize=11)
    ax.text(.3,1.2,'Included',rotation=90,ha='center',va='center',fontsize=11)
    save(fig,'figure2_prisma',args)
def performance(args,which):
    rows=[r for r in read('performance.csv') if r['figure']==str(which)]
    panels=list(dict.fromkeys(r['panel'] for r in rows))
    fig,axes=plt.subplots(len(panels),1,figsize=(10,4*len(panels)),squeeze=False)
    for ax,panel in zip(axes[:,0],panels):
        rs=[r for r in rows if r['panel']==panel];labels=list(dict.fromkeys(r['label'] for r in rs))
        for r in rs:
            x=float(r['value']);y=labels.index(r['label']);met=r['metric']
            y+= -.1 if met=='Sensitivity' else .1 if met=='Specificity' else 0
            color='#777777' if r['comparator']=='1' else '#0072b2' if met!='Specificity' else '#d55e00'
            marker='s' if met=='Specificity' else 'o'
            if r['interval_type']=='wilson_95ci':lo,hi=wilson(r['numerator'],r['denominator'])
            elif r['lower']:lo,hi=float(r['lower']),float(r['upper'])
            else:lo=hi=x
            if not 0<=lo<=x<=hi<=1:raise ValueError(r)
            ax.errorbar(x,y,xerr=[[x-lo],[hi-x]],fmt=marker,color=color,capsize=3,label=met)
        ax.set_yticks(range(len(labels)),labels);ax.set_ylim(len(labels)-.5,-.5)
        ax.set_xlim(0 if which!=4 else .65,1.02);ax.set_title(panel,loc='left',fontsize=12,weight='bold')
        kinds=set(r['interval_type'] for r in rs)
        ax.set_xlabel('AUROC ± cross-fold SD (not a confidence interval)' if 'cross_fold_sd' in kinds else 'AUROC with reported 95% CI where available' if which==4 else 'Estimate with 95% confidence interval')
        ax.grid(axis='x',alpha=.18)
        if which!=4:
            h,l=ax.get_legend_handles_labels();u=dict(zip(l,h));ax.legend(u.values(),u.keys(),loc='lower left',fontsize=8)
        for s in ['top','right']:ax.spines[s].set_visible(False)
    fig.tight_layout()
    save(fig,{3:'figure3_af_accuracy',4:'figure4_discrimination','A5':'appendix5_secondary_results'}[which],args)
def upload_copies(args):
    out=args.output/'JMIR_upload_ready';out.mkdir(exist_ok=True)
    for p in args.output.glob('*.png'):
        im=Image.open(p).convert('RGB');im.thumbnail((1200,1200),Image.Resampling.LANCZOS)
        im.save(out/p.name,dpi=(300,300),optimize=True)
        assert (out/p.name).stat().st_size<5_000_000
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dpi',type=int,default=600);p.add_argument('--output',type=Path,default=ROOT/'figures')
    p.add_argument('--appendix',action='store_true',help='Also visualize Appendix 5 Table S1 (new optional plot).')
    args=p.parse_args()
    if args.dpi<300:p.error('Use at least 300 DPI for master exports.')
    args.output.mkdir(parents=True,exist_ok=True)
    framework(args);prisma(args);performance(args,3);performance(args,4)
    subprocess.run([sys.executable,str(ROOT/'scripts/plot_appraisals.py'),'--dpi',str(args.dpi),'--output',str(args.output)],check=True)
    if args.appendix:performance(args,'A5')
    upload_copies(args)
    print('Figures saved to',args.output)
if __name__=='__main__':main()
