drop function if exists get_product_rest;

create or replace function get_product_rest(
    current_product_id bigint, city_slug text
) returns int
language plpgsql
as
$$
declare
    rest int;
BEGIN
    if city_slug is NULL THEN
        city_slug = 'almaty';
    end if;
    SELECT
        r.quantity
    INTO
        rest
    FROM
        shop_rest r
        INNER JOIN shop_product pr on r.product_id = pr.id and pr.id = current_product_id
        INNER JOIN shop_storehouse ss on r.storehouse_id = ss.id
        INNER JOIN location_city_storehouses lcs on ss.id = lcs.storehouse_id
        INNER JOIN location_city lc on lcs.city_id = lc.id
    WHERE
        lc.slug = city_slug;
    if rest is NULL then
        rest = 0;
    end if;
    return rest;
END
$$;


