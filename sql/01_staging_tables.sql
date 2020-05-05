drop table [dbo].[stg_ips_group_parking_meter_inventory_2020];
CREATE TABLE [dbo].[stg_ips_group_parking_meter_inventory_2020](
	[active] [varchar](250) NULL,
	[areaname] [varchar](250) NULL,
	[configid] [varchar](250) NULL,
	[lat] [varchar](250) NULL,
	[long] [varchar](250) NULL,
	[meter_number] [varchar](250) NULL,
	[subareaname] [varchar](250) NULL,
	[zonename] [varchar](250) NULL
) ON [PRIMARY];

drop table [dbo].[stg_parking_tranxn_2018];
CREATE TABLE [dbo].[stg_parking_tranxn_2018](
	[parkingenddate] [varchar](250) NULL,
	[parkingstartdate] [varchar](250) NULL,
	[pole] [varchar](250) NULL,
	[transactiontype] [varchar](250) NULL);

drop table [dbo].[stg_parking_tranxn_2019];
CREATE TABLE [dbo].[stg_parking_tranxn_2019](
	[parkingenddate] [varchar](250) NULL,
	[parkingstartdate] [varchar](250) NULL,
	[pole] [varchar](250) NULL,
	[transactiontype] [varchar](250) NULL);

drop table [dbo].[stg_parking_tranxn_2015_2017];
CREATE TABLE [dbo].[stg_parking_tranxn_2015_2017](
	[parkingenddate] [varchar](250) NULL,
	[parkingstartdate] [varchar](250) NULL,
	[pole] [varchar](250) NULL,
	[transactiontype] [varchar](250) NULL,
    [totalcredit] [varchar](250) NULL);

drop table [dbo].[stg_parkmobile];
CREATE TABLE [dbo].[stg_parkmobile](
	[duration] [varchar](250) NULL,
	[location] [varchar](250) NULL,
	[parking_end_date] [varchar](250) NULL,
	[parking_start_date] [varchar](250) NULL,
	[parkingamount] [varchar](250) NULL,
	[paymentdate] [varchar](250) NULL,
	[supplier] [varchar](250) NULL,
	[zone] [varchar](250) NULL);