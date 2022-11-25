drop function if exists get_product_rating;

create or replace function get_product_rating(
    current_product_id bigint
) returns numeric
language plpgsql
as
$$
declare
    rating numeric;
BEGIN
    SELECT
        AVG(sp.stars)
    INTO
        rating
    FROM
        shop_product p
        INNER JOIN shop_productreview sp on p.id = sp.product_id
    WHERE p.id = current_product_id;
    if rating is NULL then
        rating = 0.0;
    end if;
    return rating;
END
$$;


