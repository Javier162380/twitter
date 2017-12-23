words_file_english = open('sentiment_files/AFINN-111.txt',encoding='utf-8')
word_dict_english = {word.upper():int(score) for word,score in [line.split('\t') for line in words_file_english]}
words_file_spanish = open('sentiment_files/Redondo_words.txt', encoding='utf-8')
words_dict_spanish = {(word.split(' ')[0]).upper():float(word.split(' ')[1])
                       for word in [line.replace('\t', ' ').replace('\n', '') for line in words_file_spanish]
                       if "." in word}

