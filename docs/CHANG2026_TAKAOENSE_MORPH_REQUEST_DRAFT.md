# Draft follow-up request: machine-readable tree files and ccy3839 herbarium record

Status: draft only — not sent

## What no longer needs confirmation

The official Figure 1 image has now been recovered at high resolution. Panels B and C directly and concordantly label the six *Cirsium japonicum* var. *takaoense* samples as:

- FC / `ccy3559` — BP
- TJ / `ccy3807` — BP
- NH / `ccy3835` — BP
- WY / `ccy3560` — W
- FB / `ccy3629` — W
- LT / `ccy3839` — W

Therefore an author request is no longer needed to recover the W/BP mapping.

## Remaining purpose

A short follow-up request may still be useful for:

1. the machine-readable Figure 1/sample tree with branch lengths and support values;
2. the underlying Neighbor-Net or distance matrix, if available;
3. the exact orthogroup/gene-tree inputs used for the displayed sample topology;
4. clarification of the herbarium repository for collector number `ccy3839`.

## English email draft

**Subject:** Request for machine-readable sample tree and clarification of voucher ccy3839

Dear Dr. Chang and colleagues,

I am studying flower-colour evolution in East Asian *Cirsium* and am reusing the public transcriptome data from your 2026 paper:

“Phylotranscriptomics and genome-size evidence clarify the Taiwanese *Cirsium japonicum* complex and delimit *C. brevicaule* and allied East Asian thistles.”

I have reconciled the six *C. japonicum* var. *takaoense* vouchers to PRJNA1311153 runs and BioSamples and recovered the W/BP labels directly from Figure 1. The existing sample set contains three bluish-purple samples—FC-3559, TJ-3807 and NH-3835—and three white samples—WY-3560, FB-3629 and LT-3839.

The displayed ASTRAL tree and Neighbor-Net show informative sample-level structure. Could you please share any machine-readable files available for these analyses, especially:

- the Figure 1 species/sample tree in Newick or Nexus format;
- branch lengths and the definitions of displayed support values;
- the Neighbor-Net input distance matrix or exported network;
- retained orthogroup alignments or gene trees used for the sample topology;
- a tip-name key if labels differ from Supplementary Table S1.

I also noticed a possible herbarium discrepancy for collector number `ccy3839`:

- Supplementary Table S1 lists TCF;
- Supplementary Table S6 lists TNM.

Could you confirm whether material is deposited at TCF, TNM, or both?

I will preserve the published sample terminology, public accessions and the distinction between direct phenotype labels and evolutionary interpretation. The requested tree files would allow topology and branch-length sensitivity analyses without reconstructing numerical information from the published figure.

Thank you very much for your help.

Best regards,

Ruiqi Zhang / 張瑞琪

## Traditional Chinese draft

**主旨：請教Figure 1系統樹原始檔及ccy3839標本館資訊**

張先生／女士及共同作者您好：

我目前正在研究東亞薊屬植物花色的演化，並希望重用貴團隊2026年論文中公開的轉錄體資料：

“Phylotranscriptomics and genome-size evidence clarify the Taiwanese *Cirsium japonicum* complex and delimit *C. brevicaule* and allied East Asian thistles.”

我已將六份玉山薊 *Cirsium japonicum* var. *takaoense* 憑證標本與PRJNA1311153的run及BioSample完成一對一對應，也從Figure 1直接確認花色標記：FC-3559、TJ-3807及NH-3835為BP；WY-3560、FB-3629及LT-3839為W。

Figure 1中的ASTRAL樹與Neighbor-Net具有重要的樣本層級資訊。若方便，想請教是否能提供以下機器可讀原始檔：

- Figure 1樣本／物種樹的Newick或Nexus檔；
- branch length及圖中support value的定義；
- Neighbor-Net使用的distance matrix或匯出的network檔；
- 建立樣本樹所使用的orthogroup alignment或gene tree；
- 若tree tip名稱與Supplementary Table S1不同，對應的tip-name key。

另外，collector number `ccy3839`的標本館資訊似乎不一致：

- Supplementary Table S1記為TCF；
- Supplementary Table S6記為TNM。

想請教該標本實際保存於TCF、TNM，或兩館皆有複份？

我會保留論文原本的樣本名稱、公開accession，以及直接花色標記與演化解釋之間的區別。若能取得原始樹檔，就不必從論文圖片反推branch length或support。

非常感謝您的協助。

敬祝順心

張瑞琪 / Ruiqi Zhang

## Minimal response form

```text
Figure 1 Newick/Nexus available: yes / no
Branch lengths represent:
Support values represent:
Neighbor-Net distance/network file available: yes / no
Orthogroup alignments or gene trees available: yes / no
ccy3839 herbarium: TCF / TNM / both / other
File or repository link:
```

## Herbarium-only request variant

For TNM or TCF staff:

> Chang et al. 2026 Supplementary Table S1 records collector number ccy3839 at TCF, whereas Supplementary Table S6 records the same collector number at TNM. Could you confirm whether a sheet or duplicate is held in your collection and provide the accession/barcode or specimen image if available?

The living corolla state is already directly documented as white in Figure 1; it should not be inferred from dried petal colour.
