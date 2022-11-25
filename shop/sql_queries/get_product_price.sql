drop function if exists get_product_price;

create or replace function get_product_price(
    current_product_id bigint, city_slug text, current_storehouse_type text
) returns numeric
language plpgsql
as
$$
declare
    price numeric;
BEGIN
    if city_slug is NULL THEN
        city_slug = 'almaty';
    end if;
    SELECT
        p.price
    INTO
        price
    FROM
        shop_productprice p
        INNER JOIN shop_product pr on p.product_id = pr.id and pr.id = current_product_id
        INNER JOIN shop_storehouse ss on p.storehouse_id = ss.id
        INNER JOIN location_city_storehouses lcs on ss.id = lcs.storehouse_id and
                                                    ss.storehouse_type = current_storehouse_type
        INNER JOIN location_city lc on lcs.city_id = lc.id
    WHERE
        lc.slug = city_slug;
    if price is NULL then
        price = 0.0;
    end if;
    return price;
END
$$;


