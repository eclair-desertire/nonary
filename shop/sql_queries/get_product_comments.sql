drop function if exists get_product_comments;

create or replace function get_product_comments(
    current_product_id bigint
) returns int
language plpgsql
as
$$
declare
    comments int;
BEGIN
    SELECT
        Count(sp.id)
    INTO
        comments
    FROM
        shop_product p
        INNER JOIN shop_productreview sp on p.id = sp.product_id
    WHERE p.id = current_product_id;
    if comments is NULL then
        comments = 0;
    end if;
    return comments;
END
$$;


