import sys
class context_match_pair:
    def __init__(self,
                 compress_prompt,
                 original_prompt
                 ):
        self.compress_prompt=[item for item in compress_prompt]
        self.original_prompt=[item for item in original_prompt]
        self.match_length=0
        self.match_context=""
        self.sp1="\colorbox{green}{"
        self.sp2="}"

    def matching(self):
        label=False
        log=""
        i=0
        j=0
        length_log=[]
        matchlen=0

        self.recurf_match(
            log,
            length_log,
            label,
            matchlen,
            i,
            j,
        )

        self.match_context=self.match_context.replace("\n","\n\n").replace("%","\%")

    def recurf_match(
            self,
            log,
            length_log,
            label,
            matchlen,
            i,
            j,
    ):
        tmplen=0
        while(1):
            # print(i,j,[str1[0:i+1]],[str2[0:j+1]])
            if len(length_log)>=5:
                if sum(length_log[-5:-1])<7:
                    return False
            if i==len(self.compress_prompt):
                if label==True:
                    log+=self.sp2
                # print(matchlen)
                # print(log)
                self.match_length=matchlen
                self.match_context=log
                # sys.exit()
                # print("####")
                return True
            elif j==len(self.original_prompt):
                # print("Error",i,j,len(test1),len(test2))
                return False
            if self.compress_prompt[i]==self.original_prompt[j]:
                if label==False:
                    log+=self.sp1
                    label=True
                log+=self.original_prompt[j]
                tmplen+=1
                matchlen+=1
                i+=1
                j+=1
            else:
                if self.compress_prompt[i] in [" ","\n"]:
                    # print("####")
                    ret=self.recurf_match(
                        log,
                        length_log,
                        label,
                        matchlen,
                        i+1,
                        j,
                    )
                    if ret:
                        return True
                if label==True:
                    log+=self.sp2
                    label=False
                    if tmplen>0:
                        length_log.append(tmplen)
                log+=self.original_prompt[j]
                j+=1

if(__name__=="__main__"):

    str1="Every winter architect Kevin   Adams  would perform his early morning ritual devotion. Cloth in hand he'd head to stylish Crittall windows in East London flat where once lived - because these windows, though stylish also sopping \"You'd know to expect it - you wipe it down, open window as soon can let it puddle or rot the sills he says of moisture that used form singleglazing and thin steel frames his windows when the weather cold \"I put up it because loved them. We do all kinds things for love,?\" Not everyone who has lived with vintage steel-framed windows feels so affectionate, however Crittall Windows became synonymous both modernism - and condensation, which can lead serious problems such mould, says Mr Adams, a teaching fellow Edinburgh College While many consider such windows iconic and a key part British architectural heritage given today high prices and rising awareness around the dangers mould efficient windows have become essential Crittall, like all other companies in glazing industry has had stay relevant to survive.While many consider such windows iconic and a key part given today high prices and rising awareness around the dangers mould efficient windows have become essential Crittall, like all other companies in glazing industry has had stay relevant to survive"
    str2="Every winter, architect Kevin Adams would perform his early morning ritual of devotion. Cloth in hand, he'd head to the stylish Crittall windows in the East London flat where he once lived - because these windows, though stylish, were also sopping wet.\"You'd know to expect it - you wipe it down, you open the window as soon as you can, you don't let it puddle or rot the sills,\" he says of the moisture that used to form on the single-glazing and thin steel frames of his windows when the weather was cold. \"I put up with it because I loved them.We do all kinds of things for love, don't we?\"\nNot everyone who has lived with vintage steel-framed windows feels so affectionate towards them, however.\nCrittall Windows became synonymous both with modernism - and condensation, which can lead to serious problems such as mould, says Mr Adams, a teaching fellow at the Edinburgh College of Art.\nWhile many consider such windows iconic and a key part of British architectural heritage, given today's high energy prices and rising awareness around the dangers of mould, efficient windows have become essential.Crittall, like all other companies in the glazing industry, has had to stay relevant to survive.While many consider such windows iconic and a key part of British architectural heritage, given today's high energy prices and rising awareness around the dangers of mould, efficient windows have become essential.Crittall, like all other companies in the glazing industry, has had to stay relevant to survive."

    context_match_pair1=context_match_pair(str1,str2)
    context_match_pair1.matching()