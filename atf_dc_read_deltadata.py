
from pyspark.sql.functions import *
from pyspark.sql.types import *
import math as m
from atf.common.atf_common_functions import log_info, get_mount_path
from constants import *

def read_deltadata(dict_configdf, spark):
  log_info("Reading delta Data")
  resourcename = dict_configdf['filename']
  comparetype = dict_configdf['testquerygenerationmode']

  #dict_configdf['targetfilepath']
  log_info(f"Resource Name - {resourcename}")
  alias_name = dict_configdf['aliasname']
  log_info(f"Alias Name - {alias_name}")

  datafilter = dict_configdf['filter']
  delta_path = dict_configdf['path']
  excludecolumns = dict_configdf['excludecolumns']
  excludecolumns = str(excludecolumns)
  exclude_cols = excludecolumns.split(',')
  datafilter = str(datafilter)

  deltatable = delta_path.replace('/','.')

  log_info(f"Delta Table Path - {deltatable}")
  df = spark.table(deltatable)
  df.createOrReplaceTempView(alias_name)
  
  if dict_configdf['comparetype'] == 's2tcompare' and dict_configdf['testquerygenerationmode'] == 'Auto':
    pass   

  #   if 'dbfs' in deltatable: 
  #     descquery = 'DESCRIBE delta.`' + deltatable + '`;'
  #     col_df = spark.sql(descquery)
  #     col_df = col_df.filter((col("col_name") != "")
  #                 & (col("col_name") != "# Partition Information")
  #                 & (~col("col_name").contains("Part"))
  #                 & (col("col_name") != "Not partitioned")
  #                 & (col("col_name") != "# col_name"))
  #     columns = list(col_df.select('col_name').toPandas()['col_name'])
  #     columnlist = list(set(columns) - set(exclude_cols))
  #     columnlist.sort()
  #     columnlist = ','.join(columnlist)
  #     query_delta = "SELECT " + columnlist +  " FROM delta.`" + deltatable + "`"
  #     if len(datafilter) >=5:
  #       query_delta = query_delta + " WHERE " + datafilter
  #     log_info(f"Select Table Command statement - \n{query_delta}")
  #     df_deltadata = spark.sql(query_delta)
  #   else:
  #     deltatable = deltatable.replace('/','.')
  #     col_df = spark.table(deltatable)
  #     columns = col_df.columns
  #     columnlist = list(set(columns) - set(exclude_cols))
  #     columnlist.sort()
  #     columnlist = ','.join(columnlist)
  #     query_delta = "SELECT " + columnlist +  " FROM " + deltatable

  #     if len(datafilter) >=5:
  #       query_delta = query_delta + " WHERE " + datafilter
  #     log_info(f"Select Table Command statement - \n{query_delta}")
    
  elif dict_configdf['comparetype'] == 's2tcompare' and dict_configdf['testquerygenerationmode'] == 'Manual':
    deltatable = deltatable.replace('/','.')
    querypath = root_path+dict_configdf['querypath']
    f = open(querypath,"r")
    query_delta= f.read().splitlines()
    query_delta=' '.join(query_delta)
    querydelta = query_delta.replace(alias_name,deltatable)
    log_info(f"Select Table Command statement - \n{querydelta}")

  elif dict_configdf['comparetype'] == 'likeobjectcompare':
    log_info('Inside likeobjectcompare code')
    columns = df.columns
    columnlist = list(set(columns) - set(exclude_cols))
    columnlist.sort()
    columnlist = ','.join(columnlist)

    query_delta = "SELECT " + columnlist + " FROM "+ alias_name
    querydelta = query_delta.replace(alias_name,deltatable)

    if len(datafilter) >=5:
      query= query + " WHERE " + datafilter
    log_info(f"Select Table Command statement - \n{querydelta}")

  df_deltadata = spark.sql(querydelta)
  
  df_deltadata.printSchema()
  df_deltadata.show()
  log_info("Returning the DataFrame")

  return df_deltadata, querydelta