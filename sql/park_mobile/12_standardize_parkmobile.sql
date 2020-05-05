drop table [dbo].[transf_parkmobile];
CREATE TABLE [dbo].[transf_parkmobile](
	[transf_id] [bigint] IDENTITY(1,1) NOT NULL,
	[zone] [varchar](10) NOT NULL,
	[startdate] [datetime] NOT NULL,
	[start_floor] [datetime] NOT NULL,
	[start_ceiling] [datetime] NOT NULL,
	[enddate] [datetime] NOT NULL,
	[end_floor] [datetime] NOT NULL,
	[end_ceiling] [datetime] NOT NULL,
	[total_parking_min] [int] NOT NULL,
	[start_min] [int] NOT NULL,
	[end_min] [int] NOT NULL,
	[semihourly_min] [int] NOT NULL,
	[semihourly_min_cnt] [int] NOT NULL,
	[location] [varchar](50) NOT NULL,
	[parkingamount] [numeric](6, 2) NOT NULL,
	[paymentdate] [datetime] NOT NULL,
	[cln_id] [bigint] NOT NULL,
	[stg_id] [bigint] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[transf_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY];

drop table [dbo].[stgcfm_parkmobile];
CREATE TABLE [dbo].[stgcfm_parkmobile](
	[stg_id] [bigint] IDENTITY(1,1) NOT NULL,
	[duration] [varchar](10) NOT NULL,
	[location] [varchar](50) NOT NULL,
	[parking_start_date] [datetime] NOT NULL,
	[parking_end_date] [datetime] NOT NULL,
	[parkingamount] [numeric](6, 2) NOT NULL,
	[paymentdate] [datetime] NOT NULL,
	[supplier] [varchar](10) NOT NULL,
	[zone] [varchar](10) NOT NULL,
 CONSTRAINT [PK_stgcfm_parkmobile] PRIMARY KEY CLUSTERED 
(
	[stg_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY];

INSERT INTO [dbo].[stgcfm_parkmobile]
           ([duration]
           ,[location]
           ,[parking_start_date]
           ,[parking_end_date]
           ,[parkingamount]
           ,[paymentdate]
           ,[supplier]
           ,[zone])
SELECT
	 trim([duration])
      ,trim([location])
      ,cast(trim([parking_start_date]) as datetime)
      ,cast(trim([parking_end_date]) as datetime)
      ,cast(trim([parkingamount]) as money)
      ,cast(trim([paymentdate]) as datetime)
      ,trim([supplier])
      ,trim([zone])
  FROM [dbo].[stg_parkmobile]
  order by
  trim([zone])
  ,cast(trim([parking_start_date]) as datetime);

