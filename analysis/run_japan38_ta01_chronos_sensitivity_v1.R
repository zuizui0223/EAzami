#!/usr/bin/env Rscript
suppressPackageStartupMessages(library(ape))
args <- commandArgs(trailingOnly=TRUE)
arg <- function(flag) { i <- match(flag,args); if (is.na(i) || i==length(args)) stop(paste('missing',flag)); args[[i+1]] }
tree_path <- arg('--tree'); outdir <- arg('--outdir'); dir.create(outdir, recursive=TRUE, showWarnings=FALSE)
tr <- read.tree(tree_path)
if (!'OUTGROUP_saff' %in% tr$tip.label) stop('OUTGROUP_saff missing')
tr <- drop.tip(tr,'OUTGROUP_saff'); if (Ntip(tr) != 39) stop('expected 39 focal biological tips')
anchor_tips <- c('J38S015','J38S036'); if (!all(anchor_tips %in% tr$tip.label)) stop('TA01 endpoint tips missing')
anchor_node <- getMRCA(tr, anchor_tips); if (is.null(anchor_node)) stop('TA01 MRCA unresolved')
ages <- c(1.85,2.27,2.69); lambdas <- c(0.1,1,10); models <- c('correlated','relaxed')
rows <- list(); k <- 0
for (age in ages) for (model in models) for (lambda in lambdas) {
  k <- k + 1; scenario <- sprintf('TA01_age%.2f_%s_lambda%s',age,model,format(lambda,scientific=FALSE,trim=TRUE))
  cal <- makeChronosCalib(tr,node=anchor_node,age.min=age,age.max=age,soft.bounds=FALSE)
  fit <- try(chronos(tr,lambda=lambda,model=model,quiet=TRUE,calibration=cal,control=chronos.control(iter.max=20000,eval.max=20000)),silent=TRUE)
  if (inherits(fit,'try-error')) { rows[[k]] <- data.frame(scenario=scenario,age_ma=age,model=model,lambda=lambda,status='failed',root_age_ma=NA,anchor_age_recovered_ma=NA,tip_depth_range=NA,convergence=NA,pl_loglik=NA,error=as.character(fit)); next }
  depths <- node.depth.edgelength(fit); tip_depth <- depths[seq_len(Ntip(fit))]; root_age <- max(tip_depth); anchor_age_recovered <- root_age - depths[anchor_node]
  conv <- attr(fit,'convergence'); if (is.null(conv)) conv <- NA; pll <- attr(fit,'PL-Loglik'); if (is.null(pll)) pll <- NA
  write.tree(fit,file=file.path(outdir,paste0(scenario,'.nwk')))
  rows[[k]] <- data.frame(scenario=scenario,age_ma=age,model=model,lambda=lambda,status='success',root_age_ma=root_age,anchor_age_recovered_ma=anchor_age_recovered,tip_depth_range=max(tip_depth)-min(tip_depth),convergence=as.character(conv)[1],pl_loglik=as.numeric(pll)[1],error='')
}
res <- do.call(rbind,rows); write.csv(res,file.path(outdir,'scenario_summary.csv'),row.names=FALSE,quote=TRUE); ok <- res[res$status=='success',]
root_range <- if(nrow(ok)) c(min(ok$root_age_ma),max(ok$root_age_ma)) else c(NA,NA); max_tip_range <- if(nrow(ok)) max(ok$tip_depth_range) else NA
summary_lines <- c('{',
'  "contract_version": "japan38_ta01_chronos_sensitivity_v1",',
'  "source_tree": "Japan38 Comp1061 compatibility tree; substitutions/site",',
'  "focal_tips": 39,',
'  "outgroup_pruned_before_dating": true,',
paste0('  "calibration": {"event_id": "TA01", "endpoint_tips": ["J38S015", "J38S036"], "anchor_node": ',anchor_node,', "ages_ma": [1.85, 2.27, 2.69], "source_interval_ma": [1.85, 2.69]},'),
'  "models": ["correlated", "relaxed"],','  "lambdas": [0.1, 1, 10],',
paste0('  "scenarios_total": ',nrow(res),','),paste0('  "scenarios_success": ',nrow(ok),','),
paste0('  "root_age_range_ma": [',paste(format(root_range,digits=12,scientific=FALSE),collapse=', '),'],' ,'),
paste0('  "maximum_tip_depth_range": ',format(max_tip_range,digits=12,scientific=FALSE),','),
'  "absolute_time_claim_allowed": false,','  "ecological_event_matching_allowed": false,',
'  "claim_boundary": "TA01-only penalized-likelihood sensitivity scaffold. One mappable interval anchor cannot by itself establish a confirmatory dated tree; EV01/EV02/EV03 remain external ecological-event windows, not calibrations."','}')
writeLines(summary_lines,file.path(outdir,'summary.json')); print(res); cat(paste(summary_lines,collapse='\n'),'\n')
