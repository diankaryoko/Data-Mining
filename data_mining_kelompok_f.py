# -*- coding: utf-8 -*-
"""Data Mining_Kelompok_F.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1mjsPrgPIVOQnzw-b4Sge-UjrXQyWZShq

Kelompok F : 

1. Alya Nadifa Putri (1806144342)
2. Kinanti Jati Kinasih (1806144456)
3. Ni Gusti Ayu Nyoman Anggraini L. (1806193350)
4. Dian Karyoko (1806193735)
5. Andi Renata Fadhillah (1806207841)
6. Muhamad Alchem Nuravian Permana (1806207873)
7. Anastasia Juniaty (1806208251)
8. Gilang Laksana Prawira (1806232124)

Sumber data : https://www.kaggle.com/c/ashrae-energy-prediction/data

Problem : Apakah investment yang dilakukan untuk meningkatkan efisiensi gedung benar-benar efektif atau tidak (dapat mengurangi cost dan emission)?

Untuk mencari tahu hal tersebut, akan dibandingkan pemakaian energi sebelum dan sesudah efisiensi. Akan tetapi, karena pemakaian energi sebelum efisiensi tidak diketahui, dibutuhkan model yang dapat memprediksi banyaknya energi yang digunakan (diwakilkan dengan variabel meter_reading) sebelum efisiensi gedung dilakukan. 

Dalam tugas ini akan dilakukan EDA untuk melihat variabel-variabel yang mungkin memengaruhi variabel meter_reading. Data diambil dari 1449 gedung di Amerika Serikat, Inggris, Kanada, dan lain-lain.

**Objective : Mencari tahu variabel-variabel yang memengaruhi meter_reading dan mendapatkan insight sebanyak-banyaknya**
"""

#Import package yang dibutuhkan

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Download data dan unzip file

from google_drive_downloader import GoogleDriveDownloader as gdd

gdd.download_file_from_google_drive(file_id='10yM8r4UMFYr5ugb4vcpCWDanVUxEGkII',
                                    dest_path='./ashrae-energy-prediction.zip',
                                    unzip = True)

"""# **Data : building_metadata.csv**

Keterangan :
*   site_id - Foreign key for the weather files
*   building_id - Foreign key for training.csv
*   primary_use - Indicator of the primary category of activities for the building based on EnergyStar property type definitions
*   square_feet - Gross floor area of the building
*   year_built - Year building was opened
*   floor_count - Number of floors of the building
"""

# Mengubah file csv menjadi dataframe

df1 = pd.read_csv('building_metadata.csv')
df1.head()

df1.info()

# Mengecek banyak variabel kategorik

df1['primary_use'].value_counts()

"""# **Data : weather_train.csv**

Keterangan:
*   site_id
*   air_temperature (suhu udara) - Degrees Celsius
*   cloud_coverage (cakupan awan)- Portion of the sky covered in clouds, in oktas 
*   dew_temperature (suhu embun) - Degrees Celsius
*   precip_depth_1_hr (precipitation/banyaknya air dari langit karena sebab apapun) - Millimeters 
*   sea_level_pressure (tekanan permukaan laut) - Millibar/hectopascals
*   wind_direction (arah angin) - Compass direction (0-360)
*   wind_speed (kecepatan angin) - Meters per second
"""

df2 = pd.read_csv('weather_train.csv')
df2.head()

df2.info()

"""# **Data : train.csv**

Keterangan :
*   building_id - Foreign key for the building metadata
*   meter - The meter id code. Read as {0: electricity, 1: chilledwater, 2: steam, 3: hotwater}. Not every building has all meter types.
*   timestamp - When the measurement was taken
*   meter_reading - The target variable. Energy consumption in kWh (or equivalent). Note that this is real data with measurement error, which we expect will impose a baseline level of modeling error. 

UPDATE: as discussed here, the site 0 electric meter readings are in kBTU.
"""

df3 = pd.read_csv('train.csv')
df3.head()

df3.info()

"""# **Menggabungkan Ketiga Dataframe**"""

# Menggabungkan ketiga dataframe

df_total = df3.merge(df1, on='building_id', how='left')
df_total = df_total.merge(df2, on=['site_id','timestamp'], how='left')

df_total.head()

df_total.info()

"""# **Mengganti Tipe Data dan Menambahkan Variabel**"""

# Mengubah tipe variabel timestamp menjadi datetime

import datetime
from datetime import datetime
df_total['timestamp'] = pd.to_datetime(df_total['timestamp'])

# Menambahkan jam, bulan, nama hari

df_total['hour'] = np.uint8(df_total['timestamp'].dt.hour)
df_total['month'] = np.uint8(df_total['timestamp'].dt.month)
df_total['day_name'] = df_total['timestamp'].dt.day_name()

df_total.head()

# Melihat distribusi meter_reading

sns.distplot(df_total['meter_reading'], kde=True, rug=True)

"""Akan digunakan transformasi log untuk melihat distribusi data meter_reading secara lebih jelas."""

# Menambahkan variabel natural_log ke df_total 

df_total['natural_log'] = np.log(df_total['meter_reading']+1)

# Melihat distribusi log(meter_reading)

sns.distplot(df_total['natural_log'], kde=True, rug=True)

"""Dari plot di atas, dapat terlihat bahwa log(meter_reading) berdistribusi normal (jika mengabaikan missing value)."""

# Mengubah tipe data

df_total['primary_use'] = df_total['primary_use'].astype('category')
df_total['building_id'] = df_total['building_id'].astype('category')
df_total['site_id'] = df_total['site_id'].astype('category')
df_total['cloud_coverage'] = df_total['cloud_coverage'].astype('category')
df_total['day_name'] = df_total['day_name'].astype('category')
df_total['meter'] = df_total['meter'].astype('category')

df_total.info()

"""# **Data Cleaning : Duplikasi, Noise, Outlier, dan Missing Value**

**Mengecek Duplikasi Data**
"""

# Mengecek duplikasi data

df_total.duplicated().sum()

"""**Mengecek Noise Data**"""

# Mengecek noise (akan dilihat dari nilai min max)

# square_feet tidak boleh negatif 
# air_temperature dan dew_tempature : range sekitar (-20, 40)
# wind_direction : rangenya 0-360
# wind_speed tidak boleh negatif  
# sea_level_pressure : range 950 - 1050 (https://www.e-education.psu.edu/meteo3/l6_p3.html#:~:text=This%20is%20where%20knowing%20the%20typical%20range%20of,or%20an%20extremely%20strong%20Arctic%20high%20in%20winter%29.)
# meter_reading tidak boleh negatif

df_total.describe()

"""**Mengecek Outlier**

Selanjutnya akan dilakukan deteksi *outlier*. Deteksi *outlier* dilakukan terlebih dahulu sebelum imputasi *missing value* agar *outlier* tidak memengaruhi metode imputasi. Deteksi *outlier* akan dilakukan dengan metode *interquartile*. Metode ini dipilih karena penggunaannya yang praktis dan tidak membutuhkan banyak asumsi (non-parametrik).

Akan tetapi, metode interquartile tidak dapat diterapkan pada variabel precip_depth_1_hr, karena Q1=Q2=Q3=0. Oleh karena itu, sebelum melakukan deteksi dan menyingkirkan outlier, akan dilihat banyaknya *zero values* di variabel precip_depth_1_hr.
"""

# Mengecek banyaknya zero values di variabel precip_depth_1_hr

df_total['precip_depth_1_hr'].isin([0]).sum()

"""Walaupun banyak pengamatan yang berisi *zero values* pada variabel precip_depth_1_hr, tetapi nilai 0 untuk variabel tersebut masih masuk akal, sehingga tidak akan kita kategorikan sebagai *missing value*. Metode interquartile tidak akan diterapkan pada variabel ini agar nilai-nilai tidak 0 tetap terjaga."""

# Meremove outlier meter_reading

Q1 = df_total['meter_reading'].quantile(0.25)
Q3 = df_total['meter_reading'].quantile(0.75)
IQR = Q3 - Q1
df_total.drop(df_total[(df_total.meter_reading < (Q1-1.5*IQR)) | (df_total.meter_reading > (Q3+1.5*IQR))].index, inplace = True)

# Meremove outlier square_feet

Q1 = df1['square_feet'].quantile(0.25)
Q3 = df1['square_feet'].quantile(0.75)
IQR = Q3 - Q1
df_total.drop(df_total[(df_total.square_feet < (Q1-1.5*IQR)) | (df_total.square_feet > (Q3+1.5*IQR))].index, inplace = True)

# Meremove outlier air_temperature

Q1 = df2['air_temperature'].quantile(0.25)
Q3 = df2['air_temperature'].quantile(0.75)
IQR = Q3 - Q1
df_total.drop(df_total[(df_total.air_temperature < (Q1-1.5*IQR)) | (df_total.air_temperature > (Q3+1.5*IQR))].index, inplace = True)

# Meremove outlier dew_temperature

Q1 = df2['dew_temperature'].quantile(0.25)
Q3 = df2['dew_temperature'].quantile(0.75)
IQR = Q3 - Q1
df_total.drop(df_total[(df_total.dew_temperature < (Q1-1.5*IQR)) | (df_total.dew_temperature > (Q3+1.5*IQR))].index, inplace = True)

# Meremove outlier sea_level_pressure

Q1 = df2['sea_level_pressure'].quantile(0.25)
Q3 = df2['sea_level_pressure'].quantile(0.75)
IQR = Q3 - Q1
df_total.drop(df_total[(df_total.sea_level_pressure < (Q1-1.5*IQR)) | (df_total.sea_level_pressure > (Q3+1.5*IQR))].index, inplace = True)

# Meremove outlier wind_direction

Q1 = df2['wind_direction'].quantile(0.25)
Q3 = df2['wind_direction'].quantile(0.75)
IQR = Q3 - Q1
df_total.drop(df_total[(df_total.wind_direction < (Q1-1.5*IQR)) | (df_total.wind_direction > (Q3+1.5*IQR))].index, inplace = True)

# Meremove outlier wind_speed

Q1 = df2['wind_speed'].quantile(0.25)
Q3 = df2['wind_speed'].quantile(0.75)
IQR = Q3 - Q1
df_total.drop(df_total[(df_total.wind_speed < (Q1-1.5*IQR)) | (df_total.wind_speed > (Q3+1.5*IQR))].index, inplace = True)

# Melihat banyaknya data setelah outlier diremove

df_total.shape

"""**Mengecek Missing Value**"""

# Mengecek missing value

df_total.isnull().sum()

"""Karena floor_count memiliki missing value >80% dan variabel year_built memiliki missing value >50%, maka kedua variabel tersebut akan di drop."""

df_total.drop(labels = 'year_built', axis = 1, inplace = True)

df_total.drop(labels = 'floor_count', axis = 1, inplace = True)

"""Salah satu cara yang paling mudah dan umum digunakan untuk me-*replace missing value* adalah menggantinya dengan *mean* atau median. Akan tetapi, karena data ini adalah data runtun waktu, mengganti *missing value* dengan *mean* atau median akan menjadi kurang akurat, terlebih jika data tersebut tidak stasioner. 

Oleh karena itu, kami akan menggunakan metode interpolasi linier untuk me-*replace* data yang hilang. Metode interpolasi linier digunakan karena ekonomis (algoritmanya tidak terlalu rumit), efisien, dan terbukti memiliki performa lebih baik daripada interpolasi non-linier di kebanyakan kasus untuk memprediksi *missing value* (Gnauk, 2004). 
"""

# Mengganti missing value pada variabel numerik dengan interpolasi linier

df_total['air_temperature'].interpolate(method='linear', direction = 'both', inplace = True)
df_total['dew_temperature'].interpolate(method='linear', direction = 'both', inplace = True)
df_total['precip_depth_1_hr'].interpolate(method='linear', direction = 'both', inplace = True)
df_total['sea_level_pressure'].interpolate(method='linear', direction = 'both', inplace = True)
df_total['wind_direction'].interpolate(method='linear', direction = 'both', inplace = True)
df_total['wind_speed'].interpolate(method='linear', direction = 'both', inplace = True)

# Mengganti missing value di cloud_coverage dengan modus
df_total['cloud_coverage'] = df_total['cloud_coverage'].fillna(df_total['cloud_coverage'].mode()[0])

# Mengecek jumlah missing value setelah melakukan imputasi

df_total.isnull().sum()

# Menghitung persentase missing value

1933/16121412

"""Karena missing value di variabel precip_depth_1_hr masih ada bahkan setelah dilakukan imputasi, maka row yang memuat missing value tersebut akan di drop. Karena jumlahnya sedikit (hanya 0.0001% dari total seluruh pengamatan), maka hal ini tidak akan terlalu memengaruhi hasil akhir secara keseluruhan, dan data yang tersisa masih cukup representatif."""

# Men-drop row dengan missing value

df_total.dropna(inplace = True)

# Memeriksa jumlah missing value setelah imputasi dan drop

df_total.isnull().sum()

"""Catatan :
Pada variabel meter_reading, terlihat seolah-olah tidak ada missing value. Akan tetapi, jika diperhatikan lebih lanjut, ada beberapa missing value sebagai berikut:
1.   Data hilang 3-5 bulan pertama (Januari - Juni 2016)
2.   Data hilang di tengah-tengah


"""

# Hilangnya data 5 bulan pertama di beberapa gedung (Contoh : gedung 1, gedung 5, gedung 100) 
df3_1 = df3.loc[(df3.building_id == 1)]
sns.lineplot(x = 'timestamp', y = 'meter_reading', data = df3_1)

df3_5 = df3.loc[(df3.building_id == 5)] 
sns.lineplot(x = 'timestamp', y = 'meter_reading', data = df3_5)

df3_100 = df3.loc[(df3.building_id == 100)]
sns.lineplot(x = 'timestamp', y = 'meter_reading', data = df3_100)

# Hilangnya data di tengah-tengah tahun (Contoh : gedung 1012) 
df3_1012 = df3.loc[(df3.building_id == 1012)]
sns.lineplot(x = 'timestamp', y = 'meter_reading', data = df3_1012)

"""Karena tidak diketahui dengan pasti gedung berapa saja yang memiliki missing value di waktu apa saja, maka proses imputasi untuk missing value meter_reading harus dilakukan satu per satu. Proses tersebut cukup memakan waktu dan memori, karena ada lebih dari 1000 gedung, sehingga untuk saat ini akan dibiarkan saja. Jika memungkinkan, alangkah baiknya jika missing value pada meter_reading tersebut diimputasi satu per satu untuk meminimalkan bias yang mungkin terjadi.

# **Statistik Deskriptif, Visualisasi dan Insight Data**
"""

# Statistik Deskriptif

df_total.describe()

# Cek korelasi

corr2 = df_total.corr()
plt.figure(figsize=(12, 10))
sns.heatmap(corr2[(corr2 >= 0.5) | (corr2 <= -0.5)],
            cmap='viridis', vmax=1.0, vmin=-1.0, linewidths=0.1,
            annot=True, annot_kws={"size": 14}, square=True);

"""Dari plot di atas, dapat terlihat bahwa variabel air_temperature dan dew_temperature memiliki korelasi yang cukup kuat, yaitu 0.69. Ini mengindikasikan adanya multikolinearitas antara kedua variabel tersebut, yang perlu diperhatikan saat nanti hendak membuat model."""

# Melihat penggunaan energi per jam 

sns.lineplot(x = "hour", y = "natural_log", data = df_total)

"""Dari plot di atas, dapat dilihat bahwa ada kecenderungan rata-rata pemakaian energi naik mulai jam 5 pagi ke atas, dan mencapai puncaknya pada siang hari (sekitar pukul 11.00 sampai 15.00). Pemakaian energi cenderung menurun setelah melewati pukul 15.00, dan mencapai titik terendahnya pada pukul 3 dini hari."""

# Penggunaan energi per hari dalam seminggu

sns.boxplot(x = 'day_name', y = 'natural_log', data = df_total, palette = 'rainbow')

"""Dari plot di atas, pemakaian energi pada hari sabtu dan minggu sedikit lebih rendah daripada hari-hari lainnya. Ini adalah hal yang wajar, mengingat sabtu dan minggu adalah *weekend* dan kebanyakan kantor/sekolah/institusi tidak beroperasi."""

# Melihat pemakaian energi untuk meter 0 (Electricity)

df_total.loc[(df_total.meter == 0)]
sns.lineplot(x = 'timestamp', y = 'meter_reading', data = df_total.loc[(df_total.meter == 0)])

"""Dari plot di atas diketahui bahwa pemakaian energi untuk listrik dari semua gedung pada 5 bulan pertama cenderung lebih rendah. Hal ini dicurigai disebabkan oleh banyaknya missing value pada 5 bulan pertama pada meter 0 (yang diketahui setelah menjalankan plot meter 0 untuk beberapa gedung)."""

# Melihat pemakaian energi untuk meter 1 (Chilled Water)

sns.lineplot(x = 'timestamp', y = 'meter_reading', data = df_total.loc[(df_total.meter == 1)])

"""Dari plot di atas, terlihat bahwa pemakaian energi tertinggi untuk air dingin (chilled water) kira-kira jatuh pada bulan 7 sampai 9. Bulan 7 sampai 9 merupakan musim panas di Amerika, sehingga wajar jika pemakaian air dingin meningkat. Pemakaian energi terendah ada pada bulan 12 sampai bulan 2. Bulan 12 sampai bulan 2 merupakan musim dingin di Amerika, sehingga air dingin tidak terlalu dibutuhkan."""

# Melihat pemakaian energi untuk meter 2 (Steam)

sns.lineplot(x = 'timestamp', y = 'meter_reading', data = df_total.loc[(df_total.meter == 2)])

"""Jika dibandingkan dengan kedua plot sebelumnya, plot pertama berada di range 60 sampai 140, plot kedua berada di 50 sampai 250, sementara plot ketiga berada di range 100 sampai 300. Dengan demikian, pemakaian energi untuk steam cenderung lebih tinggi jika dibandingkan dengan listrik dan air dingin. Jika range pemakaian energi untuk air panas di bawah 100 sampai 300, maka steam memiliki kecenderungan untuk menjadi kebutuhan yang paling menghabiskan energi dari keempat jenis meter. Pemakaian energi yang tinggi ini kemungkinan disebabkan karena steam merupakan alat multifungsi yang biasa dipakai di gedung-gedung untuk menghangatkan atau mendinginkan udara, serta dapat digunakan pula untuk proses sterilisasi di rumah sakit dan pabrik-pabrik.  """

# Melihat pemakaian energi untuk meter 3 (Hot Water)

sns.lineplot(x = 'timestamp', y = 'meter_reading', data = df_total.loc[(df_total.meter == 3)])

"""Dari plot di atas, dapat terlihat bahwa pemakaian energi untuk air panas pada bulan 11 sampai bulan 3 lebih tinggi daripada pemakaian energi untuk air panas pada bulan 5 sampai bulan 9. Kemungkinan besar ini disebabkan karena bulan 11 sampai dengan bulan 2 merupakan musim dingin di Amerika, sehingga pemakaian air panas meningkat. Begitu pula dengan bulan 7 sampai bulan 9 yang merupakan musim panas, sehingga pemakaian air panas pun menurun."""

# Menghitung rata-rata pemakaian energi per primary_use

df_primary_use = df_total.groupby('primary_use').aggregate({'meter_reading':np.mean})
df_primary_use.reset_index(inplace = True)
sns.barplot(x = 'meter_reading', y = 'primary_use', data = df_primary_use)

"""Religious worship atau tempat ibadah merupakan penggunaan gedung yang paling sedikit memakai energi, karena tempat ibadah tidak beroperasi setiap hari, hanya di hari-hari tertentu saja (misalnya gereja, tempat ibadah paling umum di Amerika, beroperasi secara aktif di hari Sabtu dan Minggu). 

Penggunaan gedung yang paling banyak memakai energi adalah utility (perusahaan air, gas, atau listrik), healthcare, education, food sales/service dan manufacturing/industrial (untuk proses produksi seperti pabrik). Gedung-gedung yang digunakan untuk kebutuhan tersebut merupakan gedung-gedung yang waktu aktifnya lama (misalnya rumah sakit beroperasi 24 jam, sekolah dan pabrik beroperasi dari pagi hingga sore, dan tempat makan bisa beroperasi sampai malam) sehingga tidak mengherankan jika pemakaian energinya lebih banyak daripada gedung yang digunakan untuk kebutuhan lain. 

Selain itu, gedung-gedung dengan penggunaan tersebut juga umumnya menggunakan steam, yang dicurigai merupakan penyebab pemakaian energi terbesar.
"""

# Banyaknya data per site_id

df1['site_id'].value_counts()

# Pemakaian energi per site_id

df_total.groupby(['site_id']).aggregate({'meter_reading':np.sum}).plot(kind = 'bar')

"""Tempat yang lebih banyak mengonsumsi energi adalah tempat dengan kode site_id 2, 9, dan 14. Ketiga tempat tersebut memiliki >100 gedung, sehingga dicurgai merupakan daerah perkotaan. Keempat tempat lainnya yang memiliki gedung >100, yaitu site_id 13, 3, 15, dan 0, juga mengonsumsi energi relatif tinggi walaupun tidak setinggi ketiga tempat sebelumnya. Kemungkinan besar ketiga gedung sebelumnya berada di wilayah atau negara yang sama, karena perbedaan meter_reading yang cukup signifikan. Site 5, 7, 8, 10, 11, dan 12 mengonsumsi energi lebih sedikit dan memiliki jumlah gedung yang lebih sedikit pula, sehingga dicurigai wiliayah ini tidak terletak di pusat kota (mungkin pinggiran kota)."""

# Membuat plot meter_reading dan square_feet

sns.lineplot(x = 'square_feet', y = 'meter_reading', data = df_total)

"""Dari plot di atas, dapat terlihat bahwa pemakaian energi dan luas tanah kemungkinan berbanding lurus, karena semakin luas tanahnya, ada kecenderungan pemakaian energi juga naik.

## **Kesimpulan**

*   Ada indikasi log(meter_reading) berdistribusi normal.
*   Ada indikasi multikolinearitas antara variabel air_temperature dan dew_temperature.
*   Pemakaian energi tertinggi cenderung terjadi pada siang hari (pukul 11.00 - 15.00) dan pemakaian energi terendah cenderung terjadi pada dini hari (pukul 3.00).
*   Pemakaian energi pada hari sabtu dan minggu (weekend) cenderung lebih rendah daripada hari lainnya, meskipun demikian perbedaannya tidak terlalu signifikan.
*   Pemakaian energi tertinggi secara umum digunakan untuk steam. 
*   Pemakaian energi untuk listrik pada 5 bulan pertama lebih rendah karena ada indikasi missing value.
*   Pemakaian energi untuk air dingin cenderung naik saat bulan 7 sampai bulan 9, dan cenderung turun saat bulan 12 sampai bulan 2. Kemungkinan hal tersebut disebabkan karena bulan 7 sampai bulan 9 merupakan musim panas, sementara bulan 12 sampai bulan 2 merupakan musim dingin.
*   Pemakaian energi untuk air panas cenderung naik saat bulan 11 sampai bulan 1, dan cenderung turun saat bulan 5 sampai bulan 9. Kemungkinan hal tersebut disebabkan karena bulan 5 sampai bulan 9 merupakan musim panas, sementara bulan 11 sampai bulan 1 merupakan musim dingin.
*   Gedung yang dipakai sebagai tempat ibadah memakan energi paling sedikit jika dibandingkan dengan yang lainnya, kemungkinan disebabkan oleh waktu aktif beroperasi yang lebih singkat (hanya hari-hari tertentu saja).
*   Gedung-gedung yang dipakai untuk utility (perusahaan air, gas, dan listrik), healthcare, education, food sales and service, serta manufacturing/industrial cenderung menggunakan energi lebih banyak, kemungkinan dikarenakan waktu aktif beroperasi yang cukup lama dan pemakaian steam yang cukup memakan energi.
*   Gedung-gedung yang terletak di wilayah site_id 2, 9, dan 14 mengonsumsi energi lebih banyak daripada wilayah lainnya dan memiliki gedung >100, relatif lebih banyak daripada wilayah lainnya. Kemungkinan tiga wilayah ini merupakan pusat kota.
*   Gedung-gedung yang terletak di wilayah site_id 5, 7, 8, 10, 11, dan 12 mengonsumsi energi lebih sedikit daripada wilayah lainnya dan memiliki gedung yang relatif lebih sedikit. Kemungkinan wilayah-wilayah ini adalah pinggiran kota.
*   Ada kecenderungan pemakaian energi berbanding lurus dengan luas bangunan.
"""