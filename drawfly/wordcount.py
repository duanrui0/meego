# ********************************************************************
# Author: deep as sea
# Create by: 2023/9/13
# Description: 
# Update: Task Update Description
# ********************************************************************
# -*- coding: utf-8 -*-
# 
#                     _ooOoo_
#                    o8888888o
#                    88" . "88
#                    (| -_- |)
#                     O\ = /O
#                 ____/`---'\____
#               .   ' \\| |// `.
#                / \\||| : |||// \
#              / _||||| -:- |||||- \
#                | | \\\ - /// | |
#              | \_| ''\---/'' | |
#               \ .-\__ `-` ___/-. /
#            ___`. .' /--.--\ `. . __
#         ."" '< `.___\_<|>_/___.' >'"".
#        | | : `- \`.;`\ _ /`;.`/ - ` : | |
#          \ \ `-. \_ __\ /__ _/ .-` / /
#  ======`-.____`-.___\_____/___.-`____.-'======
#                     `=---='
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#          佛祖保佑       永无BUG
from pyspark import SparkConf, SparkContext

# 创建Spark配置和上下文
conf = SparkConf().setMaster("local").setAppName("WordCount")
sc = SparkContext(conf=conf)


# 读取文本文件并将数据转换为RDD
input_rdd = sc.textFile("input.txt")
lines = input_rdd.collect()
for line in lines:
    print(line)
words_rdd = input_rdd.flatMap(lambda line: line.split(" "))
word_counts_rdd = words_rdd.map(lambda word:(word,1))
word_counts_rdd.reduceByKey(lambda x,y:x+y )

print(word_counts_rdd)

# 停止SparkContext
sc.stop()