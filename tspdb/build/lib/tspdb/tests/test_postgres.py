
import numpy as np
from tspdb.src.database_module.sql_imp import SqlImplementation
from tspdb.src.pindex.predict import get_prediction_range, get_prediction
from tspdb.src.pindex.pindex_managment import TSPI, load_pindex
from tspdb.src.pindex.pindex_utils import  index_ts_mapper
import time
interface = SqlImplementation(driver="postgresql", host="localhost", database="querytime_test",user="aalomar",password="AAmit32lids")
import timeit
import pandas as pd
from tspdb.src.hdf_util import read_data
from tspdb.src.tsUtils import randomlyHideValues
from scipy.stats import norm
from sklearn.metrics import r2_score
def r2_var(y,y_h,X):
    average = np.mean(X**2) - np.mean(X)**2
    return 1 - sum((y-y_h)**2)/sum((y-average)**2)

def create_table_data():

	interface = SqlImplementation(driver="postgresql", host="localhost", database="querytime_test",user="aalomar",password="AAmit32lids")
	obs = np.arange(10**5).astype('float')
	means = obs
	var = np.zeros(obs.shape)
	obs_9 = randomlyHideValues(np.array(obs), 0.9)[0]
	obs_7 = randomlyHideValues(np.array(obs), 0.7)[0]
	print(obs_9)
	df = pd.DataFrame(data ={'ts':obs, 'means':  means, 'ts_9':obs_9, 'ts_7' : obs_7,'var': var  }) 
	df.to_csv('testdata/tables/ts_basic_5.csv',index_label = 'time')

	timestamps = pd.date_range('2012-10-01 00:00:00', periods = 10**5, freq='5s')
	df.index = timestamps
	df.to_csv('testdata/tables/ts_basic_ts_5_5.csv', index_label = 'time')
	

	# real time series variance constant
	data = read_data('testdata/MixtureTS2.h5')
	obs = data['obs'][:]
	means = data['means'][:]
	var = np.ones(obs.shape)
	obs_9 = randomlyHideValues(np.array(obs), 0.9)[0]
	obs_7 = randomlyHideValues(np.array(obs), 0.7)[0]
	df = pd.DataFrame(data ={'ts':obs, 'means':  means, 'ts_9':obs_9, 'ts_7' : obs_7 ,'var': var }) 
	df.index_label = 'time'
	df.to_csv('testdata/tables/MixtureTS2.csv', index_label = 'time')
	
	# real time series variance constant
	data = read_data('testdata/MixtureTS.h5')
	obs = data['obs'][:]
	means = data['means'][:]
	var = np.ones(obs.shape)
	obs_9 = randomlyHideValues(np.array(obs), 0.9)[0]
	obs_7 = randomlyHideValues(np.array(obs), 0.7)[0]
	df = pd.DataFrame(data ={'ts':obs, 'means':  means, 'ts_9':obs_9, 'ts_7' : obs_7,'var': var  }) 
	df.to_csv('testdata/tables/MixtureTS.csv', index_label = 'time')
	
	# real time series varaince harmonics
	data = read_data('testdata/MixtureTS_var_test.h5')
	obs = data['obs'][:]
	means = data['means'][:]
	var = data['var'][:]
	obs_9 = randomlyHideValues(np.array(obs), 0.9)[0]
	obs_7 = randomlyHideValues(np.array(obs), 0.7)[0]
	df = pd.DataFrame(data ={'ts':obs, 'means':  means, 'ts_9':obs_9, 'ts_7' : obs_7, 'var': var  }) 
	df.to_csv('testdata/tables/MixtureTS_var.csv', index_label = 'time')
	
def create_tables():
	interface = SqlImplementation(driver="postgresql", host="localhost", database="querytime_test",user="postgres",password="0505")
	for table in ['ts_basic_5','ts_basic_ts_5_5','mixturets2','mixturets_var']:
		df = pd.read_csv('tspdb/tests/testdata/tables/%s.csv'%table) 
		if table == 'ts_basic_ts_5_5': df['time'] = df['time'].astype('datetime64[ns]')
		interface.create_table(table, df, 'time', include_index = False)
	

def update_test(init_points = 10**4 , update_points = [1000,100,5000,10000], T = 1000, direct_var = True ,index_name = 'ts_basic_test_pindex'):
	interface = SqlImplementation(driver="postgresql", host="localhost", database="querytime_test",user="postgres",password="0505")
	df = pd.DataFrame(data ={'ts': np.arange(init_points).astype('float')}) 
	interface.create_table('ts_basic_test', df, 'row_id', index_label='row_id')
	time_series_table = ['ts_basic_test','ts', 'row_id']
	T0 = 1000
	gamma = 0.5
	k = 2
	k_var = 1
	agg_interval = 1.
	conn = interface.engine.raw_connection()
	cur = conn.cursor()
	cur.execute('''SELECT create_pindex('%s','%s','%s','%s', "T" => %s, k => %s, k_var => %s, agg_interval => %s, var_direct => %s)'''%('ts_basic_test','row_id','ts', index_name, T, k,k_var, agg_interval, direct_var))
	cur.close()
	conn.commit()
	conn.close()
	for points in update_points:
		df = pd.DataFrame(data = {'ts':np.arange(init_points,points+init_points).astype('float')}, index = np.arange(init_points,points+init_points) ) 
		interface.bulk_insert('ts_basic_test', df, index_label='row_id')
		init_points += points
		print ('successfully updated %s points' %points)
		
def ts_table_tests(init_points = 10**4 , update_points = [1000,100,5000,10000], T = 1000, direct_var = True ,index_name = 'ts_basic_ts_pindex'):
	interface = SqlImplementation(driver="postgresql", host="localhost", database="querytime_test",user="aalomar",password="AAmit32lids")
	
	df = pd.DataFrame(data ={'ts': np.arange(init_points).astype('float')}) 
	timestamps = pd.date_range('2012-10-01 00:00:00', periods = init_points+1, freq='5s')
	end = timestamps[-1]
	df.index = timestamps[:-1]
	interface.create_table('ts_basic_ts', df, 'timestamp', index_label='timestamp')
	time_series_table = ['ts_basic_ts','ts', 'timestamp']
	T0 = 1000
	gamma = 0.5
	k = 2
	k_var = 1
	TSPD = TSPI(_dir = 'C:/Program Files/PostgreSQL/10/data/', agg_interval = 5, T = T,T_var = T, rank = k, rank_var =  k_var, col_to_row_ratio = 10, index_name = index_name,gamma = gamma, interface= interface ,time_series_table = time_series_table, direct_var = direct_var )
	TSPD.create_index()
	interface = SqlImplementation(driver="postgresql", host="localhost", database="querytime_test",user="aalomar",password="AAmit32lids")
	for points in update_points:
		df = pd.DataFrame(data = {'ts':np.arange(init_points,points+init_points).astype('float')} ) 
		timestamps = pd.date_range(end, periods = points+1, freq='5s')
		end = timestamps[-1]
		df.index = timestamps[:-1]
		interface.bulk_insert('ts_basic_ts', df, index_label='timestamp')
		init_points += points
		print ('successfully updated %s points' %points)

	# start = pd.to_datetime('2015-01-01 00:00:00')
	# end = pd.to_datetime('2018-01-01 00:00:00')
	# df = pd.DataFrame(data ={'ts': np.arange(init_points).astype('float')}) 
	# timestamps= pd.DatetimeIndex(1000000000.*(np.random.randint(start.value/10**9,end.value/10**9, init_points)))
	# df.index = np.sort(timestamps)
	# interface.create_table('ts_basic_ts2', df, 'timestamp', index_label='timestamp')

	
def create_pindex_test(table_name, T,T_var, k ,k_var, direct_var,value_column= 'ts', index_name = None , agg_interval = 1., col_to_row_ratio= 10, time_column = 'row_id'):

	interface = SqlImplementation(driver="postgresql", host="localhost", database="querytime_test",user="aalomar",password="AAmit32lids")
	T0 = 1000
	gamma = 0.5
	if index_name is None: index_name = 'pindex'
	conn = interface.engine.raw_connection()
	cur = conn.cursor()
	cur.execute('''SELECT create_pindex('%s','%s','%s','%s', "T" => %s,"t_var" =>%s, k => %s, k_var => %s, agg_interval => %s, var_direct => %s)'''%(table_name,time_column, value_column, index_name, T, T_var, k,k_var, agg_interval, direct_var))
	cur.close()
	conn.commit()
	conn.close()
	

def range_prediction_queries_test(index_name, table_name, max_):
	
	T1 = [0,0,max_-10, max_-15000, max_] + list((max_+1000) * np.random.random(10))
	T2 = [10, 10**5, max_-1, max_, max_ +10] + list((max_+1000) * np.random.random(10))
	T1 = np.array(T1).astype(int)
	T2 = np.array(T2).astype(int)
	for t1_,t2_ in zip(T1,T2):
		t1,t2 = sorted([t1_,t2_])
		# print (')
		# try:
		get_prediction_range(index_name, table_name, 'ts', 'row_id', interface, int(t1),int(t2), uq = True)
		# except: print('failure to query  range between %s and %s' % (t1,t2))

def prediction_queries_test(index_name, table_name, max_):
	
	T1 = [0,max_-10, max_-1000, max_+1, max_+10] + list((max_+1000) * np.random.random(50))
	T1 = np.array(T1).astype(int)

	for t1 in T1:
		# try: 
			get_prediction(index_name, table_name, 'ts', 'row_id', interface, int(t1), uq = True)
		# except: print('failure to query  point  %s' %t1)

def prediction_queries_accuracy_test(max_, index_name = "tspdb.ts_basic2_pindex2", table_name = "ts_basic2"):
	T1 = [100000,max_-1000, max_] + list((max_-1) * np.random.random(100))
	T1 = np.array(T1).astype(int)
	
	for t1 in T1:
		print ('t = '+str(t1))
		A,_ = get_prediction(index_name, table_name, 'ts', 'row_id', interface, int(t1))
		print (t1,A )
		assert abs(A - t1) < 1e-3
	

def range_prediction_queries_accuracy_test( index_name, file_name, table_name , value_column, max_ ):
	max_ = interface.engine.execute('Select "last_TS_inc" from tspdb.'+index_name+'_meta').fetchone()[0]
	T1 = [0, max_]
	T2 = [max_, 10**5-1]
	T1 = np.array(T1).astype(int)
	T2 = np.array(T2).astype(int)
	df = pd.read_csv('testdata/tables/%s.csv'%file_name) 
	means = df['means']
	var = df['var']
	alpha = norm.ppf(1./2 + 95./200)

	for t1_,t2_ in zip(T1,T2):
		t1,t2 = sorted([t1_,t2_])
		M = np.array(interface.engine.execute("select * from predict_range(%s, %s, %s,%s, %s, uq => True)", (table_name, value_column,int(t1),int(t2),index_name)).fetchall()).astype(np.float)
		A = M[:,0]
		est_var = (abs(M[:,0] - M[:,1])/alpha)**2
		print (t1,t2,' rmse: ',np.sqrt(np.mean(np.square(A - means[t1:t2+1]))), np.sqrt(np.mean(np.square(est_var - var[t1:t2+1]))))
		print (t1,t2,'r2: ',r2_score(means[t1:t2+1],A ), r2_var(var[t1:t2+1],est_var, df['ts'][t1:t2+1]))
		# print('first ten (predicted, actual) points for var: ', [(i,j) for i,j in zip(var[t1: t1+10],est_var[:10])])
		#assert abs(np.max(A - np.arange(t1,t2+1))) < 1e-3


def prediction_queries_latency_test():
	setup = '''import numpy as np
from tspdb.src.database_module.sql_imp import SqlImplementation
from tspdb.src.pindex.predict import get_prediction_range, get_prediction
interface = SqlImplementation(driver="postgresql", host="localhost", database="querytime_test",user="aalomar",password="AAmit32lids")
	'''
	stmt1 = '''interface.engine.execute("select * from predict('ts_basic_5', 'ts', 10, 'ts_basic5_pindex', uq => false)")'''
	stmt2 = '''interface.engine.execute("select * from predict('ts_basic_5', 'ts', 10, 'ts_basic5_pindex', uq => true)")'''
	stmt3 = '''interface.engine.execute("select * from predict_range('ts_basic_5', 'ts', 10,110, 'ts_basic5_pindex', uq => False)")'''
	
	
	stmtA = '''interface.engine.execute("select ts from ts_basic_5 where time = 10") '''
	stmtB = '''interface.engine.execute("select ts from ts_basic_5 where time >= 10 and time <= 110 ") '''
	
	print ('(test1 pindex: point query )	  	imp query latency is %s that of SELECT ' %(timeit.timeit(setup = setup,stmt= stmt1, number =10000)/timeit.timeit(setup = setup,stmt= stmtA, number =10000)))
	print ('(test2 pindex: point query with uq ) 	imp query latency is %s that of SELECT ' %(timeit.timeit(setup = setup,stmt= stmt2, number =10000)/timeit.timeit(setup = setup,stmt= stmtA, number =10000)))
	print ('(test3 pindex: range query 100 points )		imp query latency is %s that of SELECT ' %(timeit.timeit(setup = setup,stmt= stmt3, number =10000)/timeit.timeit(setup = setup,stmt= stmtB, number =10000)))
		
	stmt1 = '''interface.engine.execute("select * from predict('ts_basic_5', 'ts', 99995, 'ts_basic5_pindex', uq => false)")'''
	stmt2 = '''interface.engine.execute("select * from predict('ts_basic_5', 'ts', 99995, 'ts_basic5_pindex', uq => true)")'''
	stmt3 = '''interface.engine.execute("select * from predict_range('ts_basic_5', 'ts', 99995,99995+100, 'ts_basic5_pindex', uq => False)")'''
	
	print ('(test1 pindex: point query)	  	Forecast query latency is %s that of SELECT ' %(timeit.timeit(setup = setup,stmt= stmt1, number =1000)/timeit.timeit(setup = setup,stmt= stmtB, number =1000)))
	print ('(test2 pindex: point query with uq) 	Forecast query latency is %s that of SELECT ' %(timeit.timeit(setup = setup,stmt= stmt2, number =1000)/timeit.timeit(setup = setup,stmt= stmtA, number =1000)))
	print ('(test3 pindex: range query 100 points)		Forecast query latency is %s that of SELECT ' %(timeit.timeit(setup = setup,stmt= stmt3, number =1000)/timeit.timeit(setup = setup,stmt= stmtB, number =1000)))


def main():
	# create_table_data()
	# create_tables()
	
	# ts_table_tests()
	# print('test 1')

	# update_test()
	
	# print('test 2')
	# update_test(init_points = 10**4 , update_points = [10**4, 100,1,100000,10002], T = 10000, index_name = 'haha')
	
	# # print('test 3')
	# # update_test(init_points = 10**4 , update_points = [10**4], T = 1000000, index_name = 'hahddda')
	
	# print('test 4')
	# update_test(init_points = 10**4 , T = 1000000, direct_var = False, index_name = 'hahaeee')
	
	t2 = time.time()
	create_pindex_test('mixturets_var', 10000,100000, 2, 1, True, index_name = 'mixturets_var_pindex', time_column = 'time',agg_interval = 1. )
	print ('create pindex test: basic test, time = %s seconds, %s record/s'%(time.time()-t2, (time.time()-t2)/10**4))
	print('=======================================================')
	print('SUCCESS')
	print('=======================================================')
	
	# t2 = time.time()
	# create_pindex_test('ts_basic_5', 250000,250000, 2 ,1, True, index_name = 'ts_basic5_pindex_9', value_column = 'ts_9', time_column = 'time',agg_interval = 1. )
	# print ('create pindex test: basic test, time = %s seconds, %s record/s'%(time.time()-t2, (time.time()-t2)/10**4))
	# print('=======================================================')
	# print('SUCCESS')
	# print('=======================================================')
	
	# t2 = time.time()
	# create_pindex_test('ts_basic_ts_5_5', 30000,30000, 2 ,1, True, index_name = 'ts_basic2_pindex2', time_column = 'time',agg_interval = 5. )
	# print ('create pindex test: basic test T = 10000, time = %s seconds, %s record/s'%(time.time()-t2, (time.time()-t2)/10**4))
	# print('=======================================================')
	# print('SUCCESS')
	# print('=======================================================')
	
	# t2 = time.time()
	# create_pindex_test('ts_5', 9240,9240, 2 ,1, True, index_name = 'ts_5_pindex' )
	# print ('create pindex test: T = 9240, time = %s seconds, %s record/s' %(time.time()-t2, (time.time()-t2)/10**5))
	# print('=======================================================')
	# print('SUCCESS')
	# print('=======================================================')
	# prediction_queries_latency_test()
	# t2 = time.time()
	# range_prediction_queries_accuracy_test( 'ts_basic5_pindex', 'ts_basic_5', 'ts_basic_5' , 'ts', 10**5-100 )
	# range_prediction_queries_accuracy_test( 'mixturets_var_pindex', 'mixturets_var', 'mixturets_var' , 'ts', 10**5-100 )
	
	

main()
