"""Regenerate display-only Figures 5–7; does not edit documents or judgments."""
from pathlib import Path
import csv
import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description="Plot reconciled appraisal judgments from aggregate CSVs.")
parser.add_argument("--dpi",type=int,default=600)
parser.add_argument("--output",type=Path,default=BASE/"figures")
args=parser.parse_args()
def read(name):
    with (BASE/"data"/name).open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))
DATA={"quadas":read("quadas.csv"),"probast":read("probast.csv"),"grade":read("grade.csv")}
for r in DATA["grade"]:
    r["display_codes"]=[r[k+"_display"] for k in ["rob","inconsistency","indirectness","imprecision","publication_bias"]]
OUT=args.output;OUT.mkdir(parents=True,exist_ok=True)
def save(fig,name):
    fig.tight_layout()
    for ext in ['png','pdf','svg']:fig.savefig(OUT/f'{name}.{ext}',dpi=args.dpi,facecolor='white',transparent=False)
    plt.close(fig)
def lights(rows,name,title,prob=False):
    fig,ax=plt.subplots(figsize=(11,6));ax.set_xlim(-7.8,9);ax.set_ylim(len(rows)+1,-2.4);ax.axis('off')
    ax.text(-7.7,-1.8,title,weight='bold',fontsize=15)
    keys=['participants','index_test_or_predictors','target_condition_or_outcome','analysis','overall','app_participants','app_index_or_predictors','app_target_or_outcome','app_overall']
    for j,h in enumerate(['P','Pr' if prob else 'I','O' if prob else 'T','A','Overall','P','Pr' if prob else 'I','O' if prob else 'T','Overall']):ax.text(j,-.45,h,ha='center',fontsize=11)
    ax.text(2,-1.1,'Development quality / evaluation risk of bias' if prob else 'Risk of bias',ha='center',fontsize=10.5)
    ax.text(6.5,-1.1,'Applicability',ha='center',fontsize=11)
    style={'low':('#38a36e','+'),'high':('#d85b59','−'),'unclear':('#edc95b','?'),'insufficient information':('#edc95b','?')}
    for i,r in enumerate(rows):
        ax.text(-7.7,i,r['display_label'],fontsize=10.5,va='center')
        for j,key in enumerate(keys):
            col,sym=style[r[key]];ax.scatter(j,i,c=col,s=210);ax.text(j,i,sym,ha='center',va='center',fontsize=12)
    ax.text(-7.7,len(rows)+.4,'P: participants; I: index test; Pr: predictors; T: target condition; O: outcome; A: analysis.',fontsize=9)
    ax.text(-7.7,len(rows)+.8,'+ Low     − High     ? Insufficient information / unclear. Rows are appraisal records, not independent studies.',fontsize=9)
    save(fig,name)
lights(DATA['quadas'],'figure5_quadas3','QUADAS-3: Risk of bias and applicability')
lights(DATA['probast'],'figure6_probast_ai','PROBAST+AI: Model development and evaluation',True)
fig,ax=plt.subplots(figsize=(9,12));ax.set_xlim(-10.5,6.4);ax.set_ylim(36,-2);ax.axis('off')
ax.text(-10.3,-1.3,'Outcome-specific GRADE evidence profiles',fontsize=14,weight='bold')
for j,h in enumerate(['RoB','Inc','Ind','Imp','PB']):ax.text(j,-.5,h,ha='center',fontsize=10)
ax.text(4.7,-.5,'Certainty',fontsize=10)
style={'0':('#57a773','0'),'1':('#edc95b','1'),'2':('#d85b59','2'),'NA':('#d5d9de','–'),'U':('#d5d9de','?')}
for i,r in enumerate(DATA['grade']):
    label=r['id']+' '+r['outcome']
    if r['id']=='G28':label='G28 Five-minute warning, in-house AUROC'
    if r['id']=='G29':label='G29 Five-minute warning, INCART AUROC'
    for part in ['UHN','MIMICIV','KGH']:
        if r['id'].startswith('G_'+part):label=r['id']+' ECG-FM '+('MIMIC-IV machine labels' if part=='MIMICIV' else part)
    ax.text(-10.3,i,label,fontsize=9,va='center')
    for j,code in enumerate(r['display_codes']):
        col,sym=style[code];ax.scatter(j,i,c=col,s=145);ax.text(j,i,sym,ha='center',va='center',fontsize=9)
    ax.text(4.7,i,r['cert'],va='center',fontsize=9)
ax.text(-10.3,35.15,'RoB: bias; Inc: inconsistency; Ind: indirectness; Imp: imprecision; PB: publication bias.',fontsize=8.5)
ax.text(-10.3,35.65,'0/1/2: downgrade levels. Grey –: not assessable. Grey ?: undetermined. Numeric deductions unchanged.',fontsize=8.5)
save(fig,'figure7_grade')

