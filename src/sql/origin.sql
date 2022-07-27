select
	o.[record] as [person_id], 
	(select [value] from dbo.getFieldTable(o.[record], 'college_of_interest')) as [college_of_interest],
	o.[date] as [origin_date],
	a.[created] as [conversion_date],
	case when a.[id] is not null then 1 else 0 end as [conversion_ind],
	lot.[summary] as [origin_summary],
	--add origin cateogry
	
	-- repeat this for opens, clicks, pings, logins and activity
	(select sum(case when [status] in ('sent', 'open', 'complaint', 'delivered', 'click', 'optout') then 1 else null end) from [message] where [mailing] is not null and [person] = o.[record]  and ([delivered] <= a.[created] or a.[created] is null)) as [sent],

from [origin] o
left join [lookup.origin.type] lot on (o.[type] = lot.[id])
left join (select [id], [person], [created], row_number() over (partition by [person] order by [created] asc) as [rank_rev] from [application] where [person] is not null) a on (a.[person] = o.[record] and a.[rank_rev]=1)
where o.[first] = 1
and lot.[summary] != 'Application'
and (o.[record] NOT IN (select [record] from [tag] where ([tag] in ('test'))))

