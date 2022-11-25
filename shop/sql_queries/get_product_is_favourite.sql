drop function if exists get_product_is_favourite;

create or replace function get_product_is_favourite(
    current_product_id bigint, current_user_id bigint
) returns bool
language plpgsql
as
$$
declare
    is_favourite bool;
BEGIN
    is_favourite = false;
    SELECT
        true
    INTO
        is_favourite
    FROM
        auth_user_favouriteproduct fp
        INNER JOIN shop_product sp on fp.product_id = sp.id and sp.id = current_product_id
    WHERE
        fp.user_id = current_user_id;
    return is_favourite;
END
$$;


