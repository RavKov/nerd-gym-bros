from django.db import migrations

VIEW_SQL = """
CREATE OR REPLACE VIEW public.v_mobile_text_content AS
SELECT
    id,
    code,
    "group",
    text,
    created_at
FROM "gymApp_mobiletextcontent";
"""

DROP_VIEW_SQL = """
DROP VIEW IF EXISTS public.v_mobile_text_content;
"""

FUNCTION_SQL = """
CREATE OR REPLACE FUNCTION public.get_mobile_text(p_code text)
RETURNS text
LANGUAGE sql
STABLE
AS $$
    SELECT text
    FROM "gymApp_mobiletextcontent"
    WHERE code = p_code
    ORDER BY id
    LIMIT 1;
$$;
"""

DROP_FUNCTION_SQL = """
DROP FUNCTION IF EXISTS public.get_mobile_text(text);
"""

PROCEDURE_SQL = """
CREATE OR REPLACE PROCEDURE public.cleanup_expired_email_verification_codes()
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM "gymApp_emailverificationcode"
    WHERE used_at IS NULL
      AND expires_at < NOW();
END;
$$;
"""

DROP_PROCEDURE_SQL = """
DROP PROCEDURE IF EXISTS public.cleanup_expired_email_verification_codes();
"""


class Migration(migrations.Migration):
    dependencies = [
        ("gymApp", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(VIEW_SQL, reverse_sql=DROP_VIEW_SQL),
        migrations.RunSQL(FUNCTION_SQL, reverse_sql=DROP_FUNCTION_SQL),
        migrations.RunSQL(PROCEDURE_SQL, reverse_sql=DROP_PROCEDURE_SQL),
    ]
