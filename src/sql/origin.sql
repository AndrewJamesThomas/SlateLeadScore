select
	-- add basic lead info
	 o.[record] as [person_id]
	,(select [value] from [lookup.prompt] where [id] = (select top 1 [prompt] from [field] where [field] = 'college_of_interest' and [record] = o.[record] order by [timestamp] asc)) as [college_of_interest]
	
	-- add conversion/origin info
	,o.[date] as [origin_date]
	,a.[created] as [conversion_date]
	,case when a.[id] is not null then 1 else 0 end as [conversion_ind]
	,lot.[summary] as [origin_summary]
	,o.[memo] as [origin_memo]
	
	-- add aggregated stats on mailing, activity, pings, etc.
	,(select sum(case when [status] in ('sent', 'open', 'complaint', 'delivered', 'click', 'optout') then 1 else null end) from [message] where [mailing] is not null and [person] = o.[record]  and ([delivered] <= a.[created] or a.[created] is null)) as [sent]
	,(select sum(case when [status] in ('open', 'complaint', 'click', 'optout') then 1 else null end) from [message] where [mailing] is not null and [person] = o.[record]  and ([delivered] <= a.[created] or a.[created] is null)) as [sent]
	,(select sum(case when [status] in ('sent', 'open', 'complaint', 'delivered', 'click', 'optout') then 1 else null end) from [message] where [mailing] is not null and [person] = o.[record]  and ([delivered] <= a.[created] or a.[created] is null)) as [open]
	,(select sum(case when [status] in ('click') then 1 else null end) from [message] where [mailing] is not null and [person] = o.[record]  and ([delivered] <= a.[created] or a.[created] is null)) as [click]
	,(select count(distinct [url]) from [ping] where [record] = o.[record] and ([timestamp] <= a.[created] or a.[created] is null)) as [ping_count]
	,(select count(*) from [activity] where [code] = 'appointment' and [record] = o.[record] and ([date] <= a.[created] or a.[created] is null)) as [apt_count] 
	,(select count(*) from [activity] where [code] = 'chat' and [record] = o.[record] and ([date] <= a.[created] or a.[created] is null)) as [chat_count] 
	,(select count(*) from [activity] where [code] = 'email' and [record] = o.[record] and ([date] <= a.[created] or a.[created] is null)) as [email_count] 
	,(select count(*) from [activity] where [code] = 'phone call' and [record] = o.[record] and ([date] <= a.[created] or a.[created] is null)) as [phone_call_count] 
	,(select count(*) from [activity] where [code] = 'walkin' and [record] = o.[record] and ([date] <= a.[created] or a.[created] is null)) as [walkin_count] 

-- start with origin data
from [origin] o
left join [lookup.origin.type] lot on (o.[type] = lot.[id])
-- join to application table (only use first application)
left join (select [id], [person], [created], row_number() over (partition by [person] order by [created] asc) as [rank_rev] from [application] where [person] is not null) a on (a.[person] = o.[record] and a.[rank_rev]=1)
where 1=1 
and o.[first] = 1
-- remove apps without a lead
and lot.[summary] != 'Application'
-- remove test records
and (o.[record] NOT IN (select [record] from [tag] where ([tag] in ('test'))))
