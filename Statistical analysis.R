#getwd()
#setwd('')
library(lme4)
library(nlme)

EN_comment_full<-read.csv('en_comm_cleaned(no-bot).csv',header = T)
head(EN_comment_full)
colnames(EN_comment_full)
EN_comment_full$published_date<-as.Date(EN_comment_full$published_at)
max(EN_comment_full$published_date)#2024-10-06; 

#subset 2024-04-15, 2024-07-15, 2024-09-01
EN_comment_fulla<-subset(EN_comment_full, published_date >= as.Date('2024-04-15') & published_date <= as.Date('2024-09-01'))

EN_comment_fulla$condition<-NA
for (i in 1:length(EN_comment_fulla$comment_id)) {
  if (EN_comment_fulla$published_date[i]>=as.Date('2024-06-01') & EN_comment_fulla$published_date[i]<as.Date('2024-07-15'))
  {EN_comment_fulla$condition[i]<-0}
  else if (EN_comment_fulla$published_date[i]>=as.Date('2024-07-15')) {EN_comment_fulla$condition[i]<-1}
  else {EN_comment_fulla$condition[i]<-2}
}

table(EN_comment_fulla$condition) 
EN_comment_fullb<-subset(EN_comment_fulla,condition<2)
table(EN_comment_fullb$condition)
EN_comment_fullb$condition<-as.factor(EN_comment_fullb$condition)


#reply
En_reply_full<-read.csv('en_rep_cleaned(no-bot).csv',header = T)
colnames(En_reply_full)
#data cleaning before merging comments with replies
En_reply_full<-En_reply_full[,-45]
EN_comment_fulla<-EN_comment_fulla[,-6]
EN_comment_fullb<-EN_comment_fullb[,-6]
colnames(En_reply_full)[47]<-"comment_id"

En_reply_full$published_date<-as.Date(En_reply_full$published_at)

En_reply_fulla<-subset(En_reply_full, published_date >= as.Date('2024-04-15') & published_date <= as.Date('2024-09-01'))
En_reply_fulla$condition<-NA
for (i in 1:length(En_reply_fulla$comment_id)) {
  if (En_reply_fulla$published_date[i]>=as.Date('2024-06-01') & En_reply_fulla$published_date[i]<as.Date('2024-07-15'))
  {En_reply_fulla$condition[i]<-0}
  else if (En_reply_fulla$published_date[i]>=as.Date('2024-07-15')) {En_reply_fulla$condition[i]<-1}
  else {En_reply_fulla$condition[i]<-2}
}
table(En_reply_fulla$condition)
table(EN_comment_fulla$condition)
En_reply_fulla$reply<-1
EN_comment_fulla$reply<-0
En_reply_fulla$condition<-as.factor(En_reply_fulla$condition)
is.factor(EN_comment_fulla$condition)
EN_comment_fulla$condition<-as.factor(EN_comment_fulla$condition)

#combine comments with replies
CB_Full<-rbind(EN_comment_fulla,En_reply_fulla)
table(EN_comment_fulla$condition)
table(En_reply_fulla$condition)
head(CB_Full)
summary(CB_Full$condition)
is.factor(CB_Full$condition)
head(CB_Full,n=15)[,c("published_date","condition")]#check, correct

table(CB_Full$condition)
CB_Full$condition<-as.numeric(CB_Full$condition)
CB_Full$condition<-CB_Full$condition-1

CB_Full1<-subset(CB_Full,condition<2)
table(CB_Full1$condition)
CB_Full1$condition<-as.factor(CB_Full1$condition)

##MLM
#valence
Valence_f1<-lme(valence~1+condition,
                   random =~ 1 + condition |video_id, method = "ML", data = CB_Full1, na.action = na.omit)
summary(Valence_f1)# sig

Valence_f1a<-lme(valence11~1+condition,
                 random =~ 1 + condition |video_id, method = "ML", data = CB_Full1, na.action = na.omit)
summary(Valence_f1a)# sig

#sentiment
Senti_f1<-lme(sentiment~1+condition,
                 random =~ 1 + condition |video_id, method = "ML", data = CB_Full1, na.action = na.omit)
summary(Senti_f1)


Senti_f1a<-lme(sentiment11~1+condition,
              random =~ 1 + condition |video_id, method = "ML", data = CB_Full1, na.action = na.omit)
summary(Senti_f1a)

#add other control
head(CB_Full1)
CB_Full1$Media<-as.factor(CB_Full1$Media)
table(CB_Full1$Media)

CB_Full1$IntMedia<-0
CB_Full1[CB_Full1$Media==2,]$IntMedia<-1
table(CB_Full1$IntMedia)
CB_Full1$IntMedia<-as.factor(CB_Full1$IntMedia)

#MLM
Valence_int1a<-lme(valence~1+condition*IntMedia,
                 random =~ 1 + condition |video_id, method = "ML", data = CB_Full1, na.action = na.omit)
summary(Valence_int1a)

library(ggplot2)
library(effects)
effvalence <- effect(term="condition:Institution",xlevels=list(condition=c(0,1)), mod=Valence_int)
effvalence
effvalence<-as.data.frame(effvalence)
effvalence$condition<-as.factor(effvalence$condition)
effvalence$Institution<-as.factor(effvalence$Institution)
ggplot(effvalence, aes(x=condition, y=fit, group=Institution)) + 
  geom_point() + 
  geom_line(size=1.2) +
  geom_ribbon(aes(ymin=fit-se, ymax=fit+se, fill=Institution),alpha=0.3) + 
  labs(title = "Treatment by Institution", x= "Treatment", y="Valence",  fill="Institution") + theme_classic() + theme(text=element_text(size=20))

Valence11_int<-lme(valence11~1+condition*Institution,
                    random =~ 1 + condition |video_id, method = "ML", data = CB_Full1, na.action = na.omit)
summary(Valence11_int)

Senti_int<-lme(sentiment~1+condition*Institution,
                    random =~ 1 + condition |video_id, method = "ML", data = CB_Full1, na.action = na.omit)
summary(Senti_int)#all sig

Senti_int1a<-lme(sentiment~1+condition*IntMedia,
               random =~ 1 + condition |video_id, method = "ML", data = CB_Full1, na.action = na.omit)
summary(Senti_int1a)#all sig

effsenti <- effect(term="condition:IntMedia",xlevels=list(condition=c(0,1)), mod=Senti_int1a)
effsenti
effsenti<-as.data.frame(effsenti)
effsenti$condition<-as.factor(effsenti$condition)
effsenti$IntMedia<-as.factor(effsenti$IntMedia)
ggplot(effsenti, aes(x=condition, y=fit, group=IntMedia)) + 
  geom_point() + 
  geom_line(size=1.2) +
  geom_ribbon(aes(ymin=fit-se, ymax=fit+se, fill=IntMedia),alpha=0.3) + 
  labs(title = "Treatment by International Media", x= "Treatment", y="Sentiment",  fill="IntMedia") + theme_classic() + theme(text=element_text(size=20))

Senti11_int1<-lme(sentiment11~1+condition*Institution,
                 random =~ 1 + condition |video_id, method = "ML", data = CB_Full1, na.action = na.omit)
summary(Senti11_int1)

#interrupted time series
library(dplyr)
head(CB_Full1)

CB_Full1 %>% arrange(published_date) %>%
  mutate(Time = dense_rank(published_date)) %>%
  write.csv("EN_combined.csv",row.names = F)#save the dt

CB_Full2<-read.csv('EN_combined.csv',header = T)#with time factor
CB_Full2$condition<-as.factor(CB_Full2$condition)
CB_Full2$IntMedia<-0
CB_Full2[CB_Full2$Media==2,]$IntMedia<-1
table(CB_Full2$IntMedia)
tail(CB_Full2)
table(CB_Full2$Time)

Valence_ITS<-lme(valence~1+condition*IntMedia+condition*Time,
                    random =~ 1 + condition+Time |video_id, method = "ML", data = CB_Full2, na.action = na.omit)
summary(Valence_ITS)#

Senti_ITS<-lme(sentiment~1+condition*IntMedia+condition*Time,
                     random =~ 1 + condition+Time |video_id, method = "ML", data = CB_Full2, na.action = na.omit)
summary(Senti_ITS)#

#fixed effects
head(CB_Full2)
LM1<-lm(valence~condition,data = CB_Full2)
summary(LM1)

CB_Full2$lgVideo_like<-log(CB_Full2$video_like_count+1)
CB_Full2$lgChanel_follower<-log(CB_Full2$channel_subscriber_count+1)
CB_Full2$lgVideo_view<-log(CB_Full2$video_view_count+1)
CB_Full2$Media<-as.factor(CB_Full2$Media)
  
LM2<-lm(valence~condition+IntMedia+lgChanel_follower,data = CB_Full2)
summary(LM2)

LM3<-lm(valence~condition+lgChanel_follower+IntMedia+lgVideo_like+lgVideo_view, data = CB_Full2)
summary(LM3)

LM1a<-lm(sentiment~condition,data = CB_Full2)
summary(LM1a)

LM2a<-lm(sentiment~condition+lgChanel_follower+IntMedia,data = CB_Full2)
summary(LM2a)#

LM3a<-lm(sentiment~condition+lgChanel_follower+IntMedia+lgVideo_like+lgVideo_view, data = CB_Full2)
summary(LM3a)

##placebo
table(CB_Full$condition)
CB_fullP<-subset(CB_Full,condition!=1)
table(CB_fullP$condition)
CB_fullP$condition<-as.factor(CB_fullP$condition)

ValenceP<-lme(valence~1+condition,
                 random =~ 1 + condition |video_id, method = "ML", data = CB_fullP, na.action = na.omit)
summary(ValenceP)#

ValenceP2<-lme(valence11~1+condition,
                 random =~ 1 + condition |video_id, method = "ML", data = CB_fullP, na.action = na.omit)
summary(ValenceP2)

SentiP<-lme(sentiment~1+condition,
                 random =~ 1 + condition |video_id, method = "ML", data = CB_fullP, na.action = na.omit)
summary(SentiP)#

SentiP2<-lme(sentiment11~1+condition,
              random =~ 1 + condition |video_id, method = "ML", data = CB_fullP, na.action = na.omit)
summary(SentiP2)#good, condition not significant

##analyze specific emotion
colnames(CB_Full2)
Fear_full<-lme(liwc.fear~1+condition,
                 random =~ 1 + condition |video_id, method = "ML", data = CB_Full2, na.action = na.omit)
summary(Fear_full)#

Trust_full<-lme(liwc.trust~1+condition,
            random =~ 1 + condition |video_id, method = "ML", data = CB_Full2, na.action = na.omit)
summary(Trust_full)#

Surprise_full<-lme(liwc.surprise~1+condition,
             random =~ 1 + condition |video_id, method = "ML", data = CB_Full2, na.action = na.omit)
summary(Surprise_full)#


##Chinese dt
##setwd('')
CN_comment_full<-read.csv('ch_comm_cleaned(no-bot)-1031.csv',header = T)
head(CN_comment_full)
colnames(CN_comment_full)
CN_comment_full$published_date<-as.Date(CN_comment_full$published_at)
max(CN_comment_full$published_date)#2024-10-06

#subset 2024-04-15, 2024-07-15, 2024-10-01
CN_comment_fulla<-subset(CN_comment_full, published_date >= as.Date('2024-04-15') & published_date <= as.Date('2024-10-01'))
CN_comment_fulla$condition<-NA
CN_comment_fulla[CN_comment_fulla$published_date>=as.Date('2024-06-01')&CN_comment_fulla$published_date<as.Date('2024-07-15'),]$condition<-0
summary(CN_comment_fulla$condition)
CN_comment_fulla[CN_comment_fulla$published_date>=as.Date('2024-07-15')&CN_comment_fulla$published_date<as.Date('2024-09-01'),]$condition<-1
CN_comment_fulla[CN_comment_fulla$published_date>=as.Date('2024-04-15')&CN_comment_fulla$published_date<as.Date('2024-06-01'),]$condition<-2

table(CN_comment_fulla$condition)# 
CN_comment_fulla$condition<-as.numeric(CN_comment_fulla$condition)
is.numeric(CN_comment_fulla$condition)
CN_comment_fullb<-CN_comment_fulla[CN_comment_fulla$condition<2,]
table(CN_comment_fullb$condition)
CN_comment_fullb$condition<-as.factor(CN_comment_fullb$condition)

##reply
Cn_reply_full<-read.csv('ch_rep_cleaned(no-bot)-1031.csv',header = T)
Cn_reply_full$published_date<-as.Date(Cn_reply_full$published_at)
max(Cn_reply_full$published_date)
summary(Cn_reply_full$published_date)

CN_reply<-Cn_reply_full[,c("Media","video_id","published_at","sentiment","sentiment11","valence","valence11","published_date")]
summary(CN_reply$published_date)

CN_reply1<-subset(CN_reply, published_date >= as.Date('2024-04-15') & published_date <= as.Date('2024-10-01'))
head(CN_reply1)
CN_reply1$condition<-NA
CN_reply1[CN_reply1$published_date>=as.Date('2024-06-01')&CN_reply1$published_date<as.Date('2024-07-15'),]$condition<-0

CN_reply1[CN_reply1$published_date>=as.Date('2024-07-15')&CN_reply1$published_date<as.Date('2024-09-01'),]$condition<-1
CN_reply1[CN_reply1$published_date>=as.Date('2024-04-15')&CN_reply1$published_date<as.Date('2024-06-01'),]$condition<-2
summary(CN_reply1$condition)
CN_reply2<-CN_reply1[CN_reply1$condition<2,]
CN_reply2$condition<-as.factor(CN_reply2$condition)

CN_comment<-CN_comment_fullb[,c("Media","video_id", "published_at","sentiment","sentiment11","valence","valence11","published_date","condition")]
colnames(CN_comment)
colnames(CN_reply1)
summary(CN_comment$condition)
summary(CN_reply2$condition)
CN_reply2<-CN_reply2[!is.na(CN_reply2$condition),]
CN_comment<-CN_comment[!is.na(CN_comment$condition),]

#merge reply and comment datasets
CN_CB1<-rbind(CN_comment,CN_reply2)
summary(CN_CB1$condition)
write.csv(CN_CB1,"CN_combined.csv",row.names = F)

EN_dt<-read.csv('EN_combined.csv',header = T)
colnames(EN_dt)

EN_CB1<-EN_dt[,c("Media","video_id", "published_at","sentiment","sentiment11","valence","valence11","published_date","condition")]
CN_CB1$language<-0
EN_CB1$language<-1

Full_dt1<-rbind(CN_CB1,EN_CB1)
Full_dt1$language<-as.factor(Full_dt1$language)
table(Full_dt1$language)
head(Full_dt1)

#interaction with language
valence_full<-lme(valence~1+condition*language,
                  random =~ 1 + condition+language|video_id, method = "ML", data = Full_dt1, na.action = na.omit)
summary(valence_full)

library(effects)
library(ggplot2)

efflan1 <- effect(term="condition:language",xlevels=list(condition=c(0,1)), mod=valence_full)
efflan1
efflan1<-as.data.frame(efflan1)
efflan1$condition<-as.factor(efflan1$condition)
efflan1$language<-as.factor(efflan1$language)
ggplot(efflan1, aes(x=condition, y=fit, group=language)) + 
  geom_point() + 
  geom_line(size=1.2) +
  geom_ribbon(aes(ymin=fit-se, ymax=fit+se, fill=language),alpha=0.3) + 
  labs(title = "Treatment by language", x= "Treatment", y="Valence",  fill="Language") + theme_classic() + theme(text=element_text(size=20))

sentiment_full<-lme(sentiment~1+condition*language,
                    random =~ 1 + condition+language|video_id, method = "ML", data = Full_dt1, na.action = na.omit)
summary(sentiment_full)

efflan2 <- effect(term="condition:language",xlevels=list(condition=c(0,1)), mod=sentiment_full)
efflan2
efflan2<-as.data.frame(efflan2)
efflan2$condition<-as.factor(efflan2$condition)
efflan2$language<-as.factor(efflan2$language)
ggplot(efflan2, aes(x=condition, y=fit, group=language)) + 
  geom_point() + 
  geom_line(size=1.2) +
  geom_ribbon(aes(ymin=fit-se, ymax=fit+se, fill=language),alpha=0.3) + 
  labs(title = "Treatment by language", x= "Treatment", y="Sentiment",  fill="Language") + theme_classic() + theme(text=element_text(size=20))


#add robustness--different time spans
table(CB_Full2$condition)
CB_Full2$published_date<-as.Date(CB_Full2$published_date)
CB_Full2$condition2<-NA
for (i in 1:length(CB_Full2$comment_id)) {
  if (CB_Full2$published_date[i]>=as.Date('2024-06-15') & CB_Full2$published_date[i]<as.Date('2024-07-15'))
  {CB_Full2$condition2[i]<-0}
  else if (CB_Full2$published_date[i]>=as.Date('2024-07-15') & CB_Full2$published_date[i]<as.Date('2024-08-15') ) {CB_Full2$condition2[i]<-1}
  else {CB_Full2$condition2[i]<-2}
}

table(CB_Full2$condition2)
head(CB_Full2,n=30)[,c("published_date","condition2")]#check, correct
CB_Full2a<-subset(CB_Full2,condition2<2)
table(CB_Full2a$condition2)
tail(CB_Full2a)[,c("published_date","condition2")]
CB_Full2a$condition2<-as.factor(CB_Full2a$condition2)
library(lme4)
library(nlme)
Valence_time<-lme(valence~1+condition2,
                  random =~ 1 + condition2 |video_id, method = "ML", data = CB_Full2a, na.action = na.omit)
summary(Valence_time)#sig

Senti_time<-lme(sentiment~1+condition2,
                random =~ 1 + condition2 |video_id, method = "ML", data = CB_Full2a, na.action = na.omit)
summary(Senti_time)#sig

##extend to a longer time span: two&half months
##setwd('')
EN_comment_full<-read.csv('en_comm_cleaned(no-bot).csv',header = T)
head(EN_comment_full)
colnames(EN_comment_full)
EN_comment_full$published_date<-as.Date(EN_comment_full$published_at)
max(EN_comment_full$published_date)#2024-10-06; 

#2024-02-13,2024-05-01, 2024-07-15, 2024-10-01
EN_comment_full2<-subset(EN_comment_full, published_date >= as.Date('2024-02-13') & published_date <= as.Date('2024-10-01'))
max(EN_comment_full2$published_date)
EN_comment_full2$condition<-NA
head(EN_comment_full2)
for (i in 1:length(EN_comment_full2$comment_id)) {
  if (EN_comment_full2$published_date[i]>=as.Date('2024-05-01') & EN_comment_full2$published_date[i]<as.Date('2024-07-15'))
  {EN_comment_full2$condition[i]<-0}
  else if (EN_comment_full2$published_date[i]>=as.Date('2024-07-15')) {EN_comment_full2$condition[i]<-1}
  else {EN_comment_full2$condition[i]<-2}
}

table(EN_comment_full2$condition)# 514068 134150 410738 
EN_comment_full2b<-subset(EN_comment_full2,condition<2)
table(EN_comment_full2b$condition)# 514068 134150
EN_comment_full2b$condition<-as.factor(EN_comment_full2b$condition)

En_reply_full<-read.csv('en_rep_cleaned(no-bot).csv',header = T)
colnames(En_reply_full)
En_reply_full$published_date<-as.Date(En_reply_full$published_at)
En_reply_full2<-subset(En_reply_full, published_date >= as.Date('2024-02-13') & published_date <= as.Date('2024-10-01'))
max(En_reply_full2$published_date)

En_reply_full2$condition<-NA
head(En_reply_full2)
for (i in 1:length(En_reply_full2$published_date)) 
{
  if (En_reply_full2$published_date[i]>=as.Date('2024-05-01') & En_reply_full2$published_date[i]<as.Date('2024-07-15'))
  {En_reply_full2$condition[i]<-0}
  else if (En_reply_full2$published_date[i]>=as.Date('2024-07-15')) {En_reply_full2$condition[i]<-1}
  else {En_reply_full2$condition[i]<-2}
}

table(En_reply_full2$condition)# 220842  59955 170285
En_reply_full2b<-subset(En_reply_full2,condition<2)
table(En_reply_full2b$condition)# 220842  59955
En_reply_full2b$condition<-as.factor(En_reply_full2b$condition)

#combine
head(En_reply_full2b)
colnames(En_reply_full2b)
colnames(EN_comment_full2b)
##data cleaning before merging
EN_comment_full2<-EN_comment_full2[,-6]
EN_comment_full2b<-EN_comment_full2b[,-6]#
EN_comment_full2b<-EN_comment_full2b[,-9]#
En_reply_full2b<-En_reply_full2b[,-45]#
En_reply_full2b<-En_reply_full2b[,-47]#

CB_EN2<-rbind(En_reply_full2b,EN_comment_full2b)
colnames(En_reply_full2b)
colnames(EN_comment_full2b)

summary(CB_EN2$condition)
is.factor(CB_EN2$condition)
CB_EN2$condition<-as.factor(CB_EN2$condition)
head(CB_EN2,n=15)[,c("published_date","condition")]#check, correct

library(lme4)
library(nlme)
Valence_EN1<-lme(valence~1+condition,
                 random =~ 1 + condition |video_id, method = "ML", data = CB_EN2, na.action = na.omit)
summary(Valence_EN1)#

Senti_EN1<-lme(sentiment~1+condition,
               random =~ 1 + condition |video_id, method = "ML", data = CB_EN2, na.action = na.omit)
summary(Senti_EN1)