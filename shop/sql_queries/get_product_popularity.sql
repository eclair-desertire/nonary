drop function if exists get_product_popularity;

create or replace function get_product_popularity(
    current_product_id bigint
) returns int
language plpgsql
as
$$
declare
    popularity int;
BEGIN
    popularity = 0;
    SELECT
        Count(oi.id)
    INTO
        popularity
    FROM
        shop_product p
        INNER JOIN order_orderitem oi on p.id = oi.product_id
    WHERE p.id = current_product_id;
    return popularity;
END
$$;


