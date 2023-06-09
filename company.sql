PGDMP     )                    {            apteka    15.2    15.2 h    �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            �           1262    23747    apteka    DATABASE     z   CREATE DATABASE apteka WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'Russian_Russia.1251';
    DROP DATABASE apteka;
                postgres    false            �            1255    23748    calculate_order_cost_trigger()    FUNCTION     �  CREATE FUNCTION public.calculate_order_cost_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW."стоимость_заказа" := (
        SELECT (л.стоимость_производства * р.количество * 3)
        FROM "Рецепты" AS р
        JOIN "Изготовляемые лекарства" AS л ON р.id_лекарства = л.id_лекарства
        WHERE р.id_рецепта = NEW."id_рецепта"
    );

    RETURN NEW;
END;
$$;
 5   DROP FUNCTION public.calculate_order_cost_trigger();
       public          postgres    false            �            1255    23749    check_component_threshold()    FUNCTION     r  CREATE FUNCTION public.check_component_threshold() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
  component_count INTEGER;
  critical_threshold INTEGER;
  required_quantity INTEGER;
BEGIN
  -- Получение текущего количества компонента на складе и его критической нормы
  SELECT "Склад"."количество_на_складе", "Компоненты"."критическая_норма"
  INTO component_count, critical_threshold
  FROM "Склад"
  JOIN "Компоненты" ON "Склад"."id_товара_на_складе" = "Компоненты"."id_товара_на_складе"
  WHERE "Склад"."id_товара_на_складе" = NEW."id_товара_на_складе";

  -- Проверка, достигла ли компонента критической нормы или ниже
  IF component_count <= critical_threshold THEN
    -- Вычисление необходимого количества для заказа
      required_quantity := (critical_threshold * 2) + (critical_threshold - component_count);

    -- Вставка записи о заказе в таблицу Поступление
    INSERT INTO "Поступление" ("id_товара_на_складе", "количество", "дата_поступления", "дата_истечения_срока_годности")
    VALUES (NEW."id_товара_на_складе", required_quantity, CURRENT_DATE + INTERVAL '1 day', CURRENT_DATE + INTERVAL '1 year');

    -- Обновление количества на складе после заказа
    UPDATE "Склад"
    SET "количество_на_складе" = "количество_на_складе" + required_quantity
    WHERE "id_товара_на_складе" = NEW."id_товара_на_складе";
  END IF;

  RETURN NEW;
END;
$$;
 2   DROP FUNCTION public.check_component_threshold();
       public          postgres    false            �            1255    23750    check_expiration_date()    FUNCTION     �  CREATE FUNCTION public.check_expiration_date() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  -- Проверяем, если у компонента в таблице "Поступление" истек срок годности, удаляем его
  IF NEW."дата_истечения_срока_годности" < CURRENT_DATE THEN
    DELETE FROM "Поступление" WHERE "id_поступления" = NEW."id_поступления";

    -- Получаем id_товара_на_складе компонента
    DECLARE
      component_id INTEGER;
    BEGIN
      SELECT "id_товара_на_складе" INTO component_id
      FROM "Компоненты"
      WHERE "id_компонента" = (
        SELECT "id_компонента" FROM "Состав" WHERE "id_лекарства" = (
          SELECT "id_лекарства" FROM "Рецепты" WHERE "id_рецепта" = (
            SELECT "id_рецепта" FROM "Заказы" WHERE "id_заказа" = NEW."id_заказа"
          )
        )
      );

      -- Удаляем компонент со склада
      DELETE FROM "Склад" WHERE "id_товара_на_складе" = component_id;
    END;
  END IF;

  RETURN NEW;
END;
$$;
 .   DROP FUNCTION public.check_expiration_date();
       public          postgres    false                        1255    23751    update_orders_trigger()    FUNCTION     �  CREATE FUNCTION public.update_orders_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    order_row RECORD;
    component_row RECORD;
    component_quantity INTEGER;
BEGIN
    -- Получаем информацию о заказе
    FOR order_row IN
        SELECT
            "Заказы"."id_рецепта",
            "Заказы"."дата_заказа",
            "Рецепты"."id_лекарства",
            "Рецепты"."количество"
        FROM
            "Заказы"
            JOIN "Рецепты" ON "Заказы"."id_рецепта" = "Рецепты"."id_рецепта"
        WHERE
            "Заказы"."id_заказа" = NEW."id_заказа"
    LOOP
        -- Получаем информацию о компонентах лекарства
        FOR component_row IN
            SELECT
                "Состав"."id_компонента",
                "Состав"."количество_компонента",
                "Компоненты"."id_товара_на_складе"
            FROM
                "Состав"
                JOIN "Компоненты" ON "Состав"."id_компонента" = "Компоненты"."id_компонента"
            WHERE
                "Состав"."id_лекарства" = order_row."id_лекарства"
        LOOP
            -- Проверяем наличие компонента на складе
            SELECT "количество_на_складе"
            INTO STRICT component_quantity
            FROM "Склад"
            WHERE "id_товара_на_складе" = component_row."id_товара_на_складе";

            IF component_quantity >= (component_row."количество_компонента" * order_row."количество") THEN
                -- Вычитаем компоненты из склада
                UPDATE "Склад"
                SET "количество_на_складе" = "количество_на_складе" - (component_row."количество_компонента" * order_row."количество")
                WHERE "id_товара_на_складе" = component_row."id_товара_на_складе";
            ELSE
                -- Заказываем недостающие компоненты
                INSERT INTO "Поступление" (
                    "id_товара_на_складе",
                    "количество",
                    "дата_поступления",
                    "дата_истечения_срока_годности"
                )
                SELECT
                    component_row."id_товара_на_складе",
                    (component_row."количество_компонента" * order_row."количество") - component_quantity,
                    CURRENT_DATE + INTERVAL '1 day',
                    CURRENT_DATE + INTERVAL '1 day' + INTERVAL '1 year'
                FROM
                    "Склад"
                WHERE
                    "id_товара_на_складе" = component_row."id_товара_на_складе";

                -- Обновляем количество компонентов на складе
                UPDATE "Склад"
                SET "количество_на_складе" = (component_row."количество_компонента" * order_row."количество")
                WHERE "id_товара_на_складе" = component_row."id_товара_на_складе";
            END IF;
        END LOOP;
    END LOOP;
    
    -- Обновляем значение столбца "дата_изготовления" в таблице "Заказы"
    UPDATE "Заказы"
    SET "дата_изготовления" = NEW."дата_заказа" + INTERVAL '2 days'
    WHERE "id_заказа" = NEW."id_заказа";

    RETURN NEW;
END;
$$;
 .   DROP FUNCTION public.update_orders_trigger();
       public          postgres    false            
           1255    24240 *   Добавить_Заказ(integer, date) 	   PROCEDURE     �  CREATE PROCEDURE public."Добавить_Заказ"(IN "p_id_рецепта" integer, IN "p_дата_заказа" date)
    LANGUAGE plpgsql
    AS $$
DECLARE
  v_id_заказа INTEGER;
  v_дата_изготовления DATE;
  v_стоимость_заказа INTEGER;
BEGIN
  -- Вставка записи о заказе
  INSERT INTO "Заказы" ("id_рецепта", "дата_заказа")
  VALUES (p_id_рецепта, p_дата_заказа)
  RETURNING id_заказа INTO v_id_заказа;
  
  -- Получение даты изготовления заказа
  SELECT "дата_изготовления" INTO v_дата_изготовления
  FROM "Заказы"
  WHERE "id_заказа" = v_id_заказа;
  
  -- Получение стоимости заказа
  SELECT "стоимость_заказа" INTO v_стоимость_заказа
  FROM "Заказы"
  WHERE "id_заказа" = v_id_заказа;
  
  -- Вывод информации о заказе
  RAISE NOTICE 'ID заказа: %, Дата изготовления: %, Стоимость: %', v_id_заказа, v_дата_изготовления, v_стоимость_заказа;
END;
$$;
 z   DROP PROCEDURE public."Добавить_Заказ"(IN "p_id_рецепта" integer, IN "p_дата_заказа" date);
       public          postgres    false            �            1255    23753 -   ДобавитьДатуВыдачи(integer) 	   PROCEDURE       CREATE PROCEDURE public."ДобавитьДатуВыдачи"(IN "p_id_заказа" integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
  UPDATE "Заказы"
  SET "дата_выдачи" = CURRENT_DATE
  WHERE "id_заказа" = p_id_заказа;
END;
$$;
 ^   DROP PROCEDURE public."ДобавитьДатуВыдачи"(IN "p_id_заказа" integer);
       public          postgres    false            �            1255    23754 �   ДобавитьКлиента(character varying, character varying, character varying, date, character varying, character varying) 	   PROCEDURE     �  CREATE PROCEDURE public."ДобавитьКлиента"(IN "p_фамилия" character varying, IN "p_имя" character varying, IN "p_отчество" character varying, IN "p_дата_рождения" date, IN "p_адрес" character varying, IN "p_телефон" character varying)
    LANGUAGE plpgsql
    AS $$
DECLARE
  client_id INTEGER;
BEGIN
  SELECT "id_клиента" INTO client_id
  FROM "Клиенты"
  WHERE "фамилия" = p_фамилия
    AND "имя" = p_имя
    AND "отчество" = p_отчество
    AND "телефон" = p_телефон;
    
  IF client_id IS NULL THEN
    INSERT INTO "Клиенты" ("фамилия", "имя", "отчество", "дата_рождения", "адрес", "телефон")
    VALUES (p_фамилия, p_имя, p_отчество, p_дата_рождения, p_адрес, p_телефон)
    RETURNING "id_клиента" INTO client_id;
  END IF;
  
  RAISE NOTICE 'ID клиента: %', client_id;
END;
$$;
 "  DROP PROCEDURE public."ДобавитьКлиента"(IN "p_фамилия" character varying, IN "p_имя" character varying, IN "p_отчество" character varying, IN "p_дата_рождения" date, IN "p_адрес" character varying, IN "p_телефон" character varying);
       public          postgres    false                       1255    23755 z   ДобавитьЛекарство(character varying, character varying, character varying, integer, integer[], integer[]) 	   PROCEDURE     �  CREATE PROCEDURE public."ДобавитьЛекарство"(IN "p_название" character varying, IN "p_способ_применения" character varying, IN "p_способ_приготовления" character varying, IN "p_стоимость_производства" integer, IN "p_компоненты" integer[], IN "p_количество_компонентов" integer[])
    LANGUAGE plpgsql
    AS $$
DECLARE
	i INTEGER;
BEGIN
	INSERT INTO "Изготовляемые лекарства" ("название", "способ_применения", "способ_приготовления", "стоимость_производства")
	VALUES (p_название, p_способ_применения, p_способ_приготовления, p_стоимость_производства)
	RETURNING "id_лекарства" INTO i;
	
	FOR j IN 1..array_length(p_компоненты, 1)
	LOOP
		INSERT INTO "Состав" ("id_лекарства", "id_компонента", "количество_компонента")
		VALUES (i, p_компоненты[j], p_количество_компонентов[j]);
	END LOOP;
END;
$$;
 �  DROP PROCEDURE public."ДобавитьЛекарство"(IN "p_название" character varying, IN "p_способ_применения" character varying, IN "p_способ_приготовления" character varying, IN "p_стоимость_производства" integer, IN "p_компоненты" integer[], IN "p_количество_компонентов" integer[]);
       public          postgres    false                       1255    23756 J   ДобавитьРецепт(integer, integer, integer, character varying) 	   PROCEDURE     �  CREATE PROCEDURE public."ДобавитьРецепт"(IN "p_id_лекарства" integer, IN "p_количество" integer, IN "p_id_клиента" integer, IN "p_ФИО_врача" character varying)
    LANGUAGE plpgsql
    AS $$
DECLARE
  v_id_рецепта INTEGER;
BEGIN
  INSERT INTO "Рецепты" ("id_лекарства", "количество", "id_клиента", "ФИО_врача")
  VALUES (p_id_лекарства, p_количество, p_id_клиента, p_ФИО_врача)
  RETURNING id_рецепта INTO v_id_рецепта;
  
  RAISE NOTICE 'Создан рецепт с ID: %', v_id_рецепта;
END;
$$;
 �   DROP PROCEDURE public."ДобавитьРецепт"(IN "p_id_лекарства" integer, IN "p_количество" integer, IN "p_id_клиента" integer, IN "p_ФИО_врача" character varying);
       public          postgres    false                       1255    23757 �   ИзменитьИнформациюОКлиенте(integer, character varying, character varying, character varying, date, character varying, character varying) 	   PROCEDURE     M  CREATE PROCEDURE public."ИзменитьИнформациюОКлиенте"(IN "p_id_клиента" integer, IN "p_фамилия" character varying DEFAULT NULL::character varying, IN "p_имя" character varying DEFAULT NULL::character varying, IN "p_отчество" character varying DEFAULT NULL::character varying, IN "p_дата_рождения" date DEFAULT NULL::date, IN "p_адрес" character varying DEFAULT NULL::character varying, IN "p_телефон" character varying DEFAULT NULL::character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE "Клиенты"
    SET
        "фамилия" = COALESCE(p_фамилия, "фамилия"),
        "имя" = COALESCE(p_имя, "имя"),
        "отчество" = COALESCE(p_отчество, "отчество"),
        "дата_рождения" = COALESCE(p_дата_рождения, "дата_рождения"),
        "адрес" = COALESCE(p_адрес, "адрес"),
        "телефон" = COALESCE(p_телефон, "телефон")
    WHERE "id_клиента" = p_id_клиента;
END;
$$;
 Z  DROP PROCEDURE public."ИзменитьИнформациюОКлиенте"(IN "p_id_клиента" integer, IN "p_фамилия" character varying, IN "p_имя" character varying, IN "p_отчество" character varying, IN "p_дата_рождения" date, IN "p_адрес" character varying, IN "p_телефон" character varying);
       public          postgres    false                       1255    23758 m   ОбновитьЛекарство(integer, character varying, character varying, character varying, integer) 	   PROCEDURE     �  CREATE PROCEDURE public."ОбновитьЛекарство"(IN "p_id_лекарства" integer, IN "p_название" character varying, IN "p_способ_применения" character varying, IN "p_способ_приготовления" character varying, IN "p_стоимость_производства" integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
  UPDATE "Изготовляемые лекарства"
  SET
    "название" = COALESCE(p_название, "название"),
    "способ_применения" = COALESCE(p_способ_применения, "способ_применения"),
    "способ_приготовления" = COALESCE(p_способ_приготовления, "способ_приготовления"),
    "стоимость_производства" = COALESCE(p_стоимость_производства, "стоимость_производства")
  WHERE
    "id_лекарства" = p_id_лекарства;
END;
$$;
 G  DROP PROCEDURE public."ОбновитьЛекарство"(IN "p_id_лекарства" integer, IN "p_название" character varying, IN "p_способ_применения" character varying, IN "p_способ_приготовления" character varying, IN "p_стоимость_производства" integer);
       public          postgres    false                       1255    23759 S   ОбновитьРецепт(integer, integer, integer, integer, character varying) 	   PROCEDURE     �  CREATE PROCEDURE public."ОбновитьРецепт"(IN "p_id_рецепта" integer, IN "p_id_лекарства" integer, IN "p_количество" integer, IN "p_id_клиента" integer, IN "p_ФИО_врача" character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
  UPDATE "Рецепты"
  SET
    "id_лекарства" = COALESCE(p_id_лекарства, "id_лекарства"),
    "количество" = COALESCE(p_количество, "количество"),
    "id_клиента" = COALESCE(p_id_клиента, "id_клиента"),
    "ФИО_врача" = COALESCE(p_ФИО_врача, "ФИО_врача")
  WHERE
    "id_рецепта" = p_id_рецепта;
END;
$$;
 �   DROP PROCEDURE public."ОбновитьРецепт"(IN "p_id_рецепта" integer, IN "p_id_лекарства" integer, IN "p_количество" integer, IN "p_id_клиента" integer, IN "p_ФИО_врача" character varying);
       public          postgres    false                       1255    23760 !   УдалитьЗаказ(integer) 	   PROCEDURE     �   CREATE PROCEDURE public."УдалитьЗаказ"(IN "p_id_заказа" integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
  DELETE FROM "Заказы" WHERE "id_заказа" = p_id_заказа;
END;
$$;
 R   DROP PROCEDURE public."УдалитьЗаказ"(IN "p_id_заказа" integer);
       public          postgres    false                       1255    23761 %   УдалитьКлиента(integer) 	   PROCEDURE     -  CREATE PROCEDURE public."УдалитьКлиента"(IN "p_id_клиента" integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
  -- Удаление записей из таблицы "рецепты", где id_клиента равен указанному значению
  DELETE FROM "Рецепты" WHERE "id_клиента" = p_id_клиента;

  -- Удаление записи из таблицы "Клиенты" с указанным id_клиента
  DELETE FROM "Клиенты" WHERE "id_клиента" = p_id_клиента;
END;
$$;
 X   DROP PROCEDURE public."УдалитьКлиента"(IN "p_id_клиента" integer);
       public          postgres    false                       1255    23762 )   УдалитьЛекарство(integer) 	   PROCEDURE     \  CREATE PROCEDURE public."УдалитьЛекарство"(IN "p_id_лекарства" integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
  DELETE FROM "Состав" WHERE "id_лекарства" = p_id_лекарства;
  DELETE FROM "Изготовляемые лекарства" WHERE "id_лекарства" = p_id_лекарства;
END;
$$;
 `   DROP PROCEDURE public."УдалитьЛекарство"(IN "p_id_лекарства" integer);
       public          postgres    false            	           1255    23763 #   УдалитьРецепт(integer) 	   PROCEDURE     #  CREATE PROCEDURE public."УдалитьРецепт"(IN "p_id_рецепта" integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
  DELETE FROM "Заказы" WHERE "id_рецепта" = p_id_рецепта;
  DELETE FROM "Рецепты" WHERE "id_рецепта" = p_id_рецепта;
END;
$$;
 V   DROP PROCEDURE public."УдалитьРецепт"(IN "p_id_рецепта" integer);
       public          postgres    false            �            1259    23764    Компоненты    TABLE     f  CREATE TABLE public."Компоненты" (
    "id_компонента" integer NOT NULL,
    "id_товара_на_складе" integer NOT NULL,
    "название" character varying(50) NOT NULL,
    "форма" character varying(20) NOT NULL,
    "стоимость" integer NOT NULL,
    "критическая_норма" integer NOT NULL
);
 *   DROP TABLE public."Компоненты";
       public         heap    postgres    false            �            1259    23767    Поступление    TABLE     L  CREATE TABLE public."Поступление" (
    "id_поступления" integer NOT NULL,
    "id_товара_на_складе" integer NOT NULL,
    "количество" integer NOT NULL,
    "дата_поступления" date NOT NULL,
    "дата_истечения_срока_годности" date NOT NULL
);
 ,   DROP TABLE public."Поступление";
       public         heap    postgres    false            �            1259    23770 
   Склад    TABLE     �   CREATE TABLE public."Склад" (
    "id_товара_на_складе" integer NOT NULL,
    "количество_на_складе" integer NOT NULL
);
     DROP TABLE public."Склад";
       public         heap    postgres    false            �            1259    23773    Все_поступления    VIEW     �  CREATE VIEW public."Все_поступления" AS
 SELECT "Поступление"."id_поступления",
    "Поступление"."количество",
    "Поступление"."дата_поступления",
    "Поступление"."дата_истечения_срока_годности",
    "Склад"."количество_на_складе",
    "Компоненты"."id_компонента",
    "Компоненты"."название" AS "название_компонента"
   FROM ((public."Поступление"
     JOIN public."Склад" ON (("Поступление"."id_товара_на_складе" = "Склад"."id_товара_на_складе")))
     JOIN public."Компоненты" ON (("Склад"."id_товара_на_складе" = "Компоненты"."id_товара_на_складе")))
  ORDER BY "Поступление"."id_поступления";
 2   DROP VIEW public."Все_поступления";
       public          postgres    false    216    216    214    214    214    215    215    215    215    215            �            1259    23778    Заказы    TABLE     #  CREATE TABLE public."Заказы" (
    "id_заказа" integer NOT NULL,
    "id_рецепта" integer NOT NULL,
    "дата_заказа" date NOT NULL,
    "дата_изготовления" date,
    "дата_выдачи" date,
    "стоимость_заказа" integer
);
 "   DROP TABLE public."Заказы";
       public         heap    postgres    false            �            1259    23781     Заказы_id_заказа_seq    SEQUENCE     �   CREATE SEQUENCE public."Заказы_id_заказа_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 9   DROP SEQUENCE public."Заказы_id_заказа_seq";
       public          postgres    false    218            �           0    0     Заказы_id_заказа_seq    SEQUENCE OWNED BY     k   ALTER SEQUENCE public."Заказы_id_заказа_seq" OWNED BY public."Заказы"."id_заказа";
          public          postgres    false    219            �            1259    23782 -   Изготовляемые лекарства    TABLE     �  CREATE TABLE public."Изготовляемые лекарства" (
    "id_лекарства" integer NOT NULL,
    "название" character varying(50) NOT NULL,
    "способ_применения" character varying(20) NOT NULL,
    "способ_приготовления" character varying(255) NOT NULL,
    "стоимость_производства" integer NOT NULL
);
 C   DROP TABLE public."Изготовляемые лекарства";
       public         heap    postgres    false            �            1259    23785 ?   Изготовляемые лекар_id_лекарства_seq    SEQUENCE     �   CREATE SEQUENCE public."Изготовляемые лекар_id_лекарства_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 X   DROP SEQUENCE public."Изготовляемые лекар_id_лекарства_seq";
       public          postgres    false    220            �           0    0 ?   Изготовляемые лекар_id_лекарства_seq    SEQUENCE OWNED BY     �   ALTER SEQUENCE public."Изготовляемые лекар_id_лекарства_seq" OWNED BY public."Изготовляемые лекарства"."id_лекарства";
          public          postgres    false    221            �            1259    23786    Клиенты    TABLE     �  CREATE TABLE public."Клиенты" (
    "id_клиента" integer NOT NULL,
    "фамилия" character varying(20) NOT NULL,
    "имя" character varying(20) NOT NULL,
    "отчество" character varying(20) NOT NULL,
    "дата_рождения" date NOT NULL,
    "адрес" character varying(50) NOT NULL,
    "телефон" character varying(11) NOT NULL
);
 $   DROP TABLE public."Клиенты";
       public         heap    postgres    false            �            1259    23789    Рецепты    TABLE       CREATE TABLE public."Рецепты" (
    "id_рецепта" integer NOT NULL,
    "id_лекарства" integer NOT NULL,
    "количество" integer NOT NULL,
    "id_клиента" integer NOT NULL,
    "ФИО_врача" character varying(60) NOT NULL
);
 $   DROP TABLE public."Рецепты";
       public         heap    postgres    false            �            1259    23792 &   Информация_о_заказах    VIEW     �  CREATE VIEW public."Информация_о_заказах" AS
 SELECT "Заказы"."id_заказа",
    "Заказы"."дата_заказа",
    "Заказы"."стоимость_заказа",
    "Клиенты"."фамилия",
    "Клиенты"."имя",
    "Клиенты"."отчество",
    "Клиенты"."телефон",
    "Изготовляемые лекарства"."название" AS "название_лекарства"
   FROM (((public."Заказы"
     JOIN public."Рецепты" ON (("Заказы"."id_рецепта" = "Рецепты"."id_рецепта")))
     JOIN public."Клиенты" ON (("Рецепты"."id_клиента" = "Клиенты"."id_клиента")))
     JOIN public."Изготовляемые лекарства" ON (("Рецепты"."id_лекарства" = "Изготовляемые лекарства"."id_лекарства")))
  ORDER BY "Заказы"."id_заказа";
 ;   DROP VIEW public."Информация_о_заказах";
       public          postgres    false    222    223    223    223    222    222    222    222    220    220    218    218    218    218            �            1259    23797    Состав    TABLE     �   CREATE TABLE public."Состав" (
    "id_лекарства" integer NOT NULL,
    "id_компонента" integer NOT NULL,
    "количество_компонента" integer NOT NULL
);
 "   DROP TABLE public."Состав";
       public         heap    postgres    false            �            1259    23800 &   Информация_о_рецепте    VIEW     �  CREATE VIEW public."Информация_о_рецепте" AS
 SELECT "Рецепты"."id_рецепта",
    "Рецепты"."ФИО_врача",
    "Состав"."id_компонента",
    "Состав"."количество_компонента"
   FROM (public."Рецепты"
     JOIN public."Состав" ON (("Рецепты"."id_лекарства" = "Состав"."id_лекарства")))
  ORDER BY "Рецепты"."id_рецепта";
 ;   DROP VIEW public."Информация_о_рецепте";
       public          postgres    false    225    225    225    223    223    223            �            1259    23804    Клиент_и_телефон    VIEW     K  CREATE VIEW public."Клиент_и_телефон" AS
 SELECT "Клиенты"."id_клиента",
    "Клиенты"."фамилия",
    "Клиенты"."имя",
    "Клиенты"."отчество",
    "Клиенты"."телефон"
   FROM public."Клиенты"
  ORDER BY "Клиенты"."id_клиента";
 3   DROP VIEW public."Клиент_и_телефон";
       public          postgres    false    222    222    222    222    222            �            1259    23808 $   Клиенты_id_клиента_seq    SEQUENCE     �   CREATE SEQUENCE public."Клиенты_id_клиента_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 =   DROP SEQUENCE public."Клиенты_id_клиента_seq";
       public          postgres    false    222            �           0    0 $   Клиенты_id_клиента_seq    SEQUENCE OWNED BY     s   ALTER SEQUENCE public."Клиенты_id_клиента_seq" OWNED BY public."Клиенты"."id_клиента";
          public          postgres    false    228            �            1259    23809 2   Клиенты_количество_заказов    VIEW       CREATE VIEW public."Клиенты_количество_заказов" AS
 SELECT "Клиенты"."id_клиента",
    "Клиенты"."фамилия",
    "Клиенты"."имя",
    "Клиенты"."отчество",
    count("Заказы"."id_заказа") AS "количество_заказов"
   FROM ((public."Клиенты"
     LEFT JOIN public."Рецепты" ON (("Клиенты"."id_клиента" = "Рецепты"."id_клиента")))
     LEFT JOIN public."Заказы" ON (("Рецепты"."id_рецепта" = "Заказы"."id_рецепта")))
  GROUP BY "Клиенты"."id_клиента", "Клиенты"."фамилия", "Клиенты"."имя", "Клиенты"."отчество"
  ORDER BY "Клиенты"."id_клиента";
 G   DROP VIEW public."Клиенты_количество_заказов";
       public          postgres    false    223    223    218    222    222    222    222    218            �            1259    23814 0   Компоненты_id_компонента_seq    SEQUENCE     �   CREATE SEQUENCE public."Компоненты_id_компонента_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 I   DROP SEQUENCE public."Компоненты_id_компонента_seq";
       public          postgres    false    214            �           0    0 0   Компоненты_id_компонента_seq    SEQUENCE OWNED BY     �   ALTER SEQUENCE public."Компоненты_id_компонента_seq" OWNED BY public."Компоненты"."id_компонента";
          public          postgres    false    230            �            1259    23815 :   Компоненты_id_товара_на_складе_seq    SEQUENCE     �   CREATE SEQUENCE public."Компоненты_id_товара_на_складе_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 S   DROP SEQUENCE public."Компоненты_id_товара_на_складе_seq";
       public          postgres    false    214            �           0    0 :   Компоненты_id_товара_на_складе_seq    SEQUENCE OWNED BY     �   ALTER SEQUENCE public."Компоненты_id_товара_на_складе_seq" OWNED BY public."Компоненты"."id_товара_на_складе";
          public          postgres    false    231            �            1259    23816 +   Компоненты_стоимость_seq    SEQUENCE     �   CREATE SEQUENCE public."Компоненты_стоимость_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 D   DROP SEQUENCE public."Компоненты_стоимость_seq";
       public          postgres    false    214            �           0    0 +   Компоненты_стоимость_seq    SEQUENCE OWNED BY     �   ALTER SEQUENCE public."Компоненты_стоимость_seq" OWNED BY public."Компоненты"."стоимость";
          public          postgres    false    232            �            1259    24235    Лекарства    VIEW     0  CREATE VIEW public."Лекарства" AS
 SELECT "Изготовляемые лекарства"."id_лекарства",
    "Изготовляемые лекарства"."название",
    "Изготовляемые лекарства"."способ_применения",
    ("Изготовляемые лекарства"."стоимость_производства" * 3) AS "стоимость"
   FROM public."Изготовляемые лекарства"
  ORDER BY "Изготовляемые лекарства"."id_лекарства";
 '   DROP VIEW public."Лекарства";
       public          postgres    false    220    220    220    220            �            1259    23817 %   Наличие_компонентов    VIEW       CREATE VIEW public."Наличие_компонентов" AS
 SELECT "Склад"."id_товара_на_складе",
    "Компоненты"."название",
    "Компоненты"."форма",
    "Склад"."количество_на_складе"
   FROM (public."Склад"
     JOIN public."Компоненты" ON (("Склад"."id_товара_на_складе" = "Компоненты"."id_товара_на_складе")))
  ORDER BY "Склад"."id_товара_на_складе";
 :   DROP VIEW public."Наличие_компонентов";
       public          postgres    false    214    216    216    214    214            �            1259    23821 4   Поступление_id_поступления_seq    SEQUENCE     �   CREATE SEQUENCE public."Поступление_id_поступления_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 M   DROP SEQUENCE public."Поступление_id_поступления_seq";
       public          postgres    false    215            �           0    0 4   Поступление_id_поступления_seq    SEQUENCE OWNED BY     �   ALTER SEQUENCE public."Поступление_id_поступления_seq" OWNED BY public."Поступление"."id_поступления";
          public          postgres    false    234            �            1259    23822 <   Поступление_id_товара_на_складе_seq    SEQUENCE     �   CREATE SEQUENCE public."Поступление_id_товара_на_складе_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 U   DROP SEQUENCE public."Поступление_id_товара_на_складе_seq";
       public          postgres    false    215            �           0    0 <   Поступление_id_товара_на_складе_seq    SEQUENCE OWNED BY     �   ALTER SEQUENCE public."Поступление_id_товара_на_складе_seq" OWNED BY public."Поступление"."id_товара_на_складе";
          public          postgres    false    235            �            1259    23823 $   Рецепты_id_рецепта_seq    SEQUENCE     �   CREATE SEQUENCE public."Рецепты_id_рецепта_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 =   DROP SEQUENCE public."Рецепты_id_рецепта_seq";
       public          postgres    false    223            �           0    0 $   Рецепты_id_рецепта_seq    SEQUENCE OWNED BY     s   ALTER SEQUENCE public."Рецепты_id_рецепта_seq" OWNED BY public."Рецепты"."id_рецепта";
          public          postgres    false    236            �            1259    23824 6   Самое_заказываемое_лекарство    VIEW     *  CREATE VIEW public."Самое_заказываемое_лекарство" AS
 SELECT "Изготовляемые лекарства"."id_лекарства",
    "Изготовляемые лекарства"."название",
    count(*) AS "количество_заказов"
   FROM ((public."Заказы"
     JOIN public."Рецепты" ON (("Заказы"."id_рецепта" = "Рецепты"."id_рецепта")))
     JOIN public."Изготовляемые лекарства" ON (("Рецепты"."id_лекарства" = "Изготовляемые лекарства"."id_лекарства")))
  GROUP BY "Изготовляемые лекарства"."id_лекарства", "Изготовляемые лекарства"."название"
  ORDER BY (count(*)) DESC
 LIMIT 3;
 K   DROP VIEW public."Самое_заказываемое_лекарство";
       public          postgres    false    220    220    223    218    223            �            1259    23829 0   Склад_id_товара_на_складе_seq    SEQUENCE     �   CREATE SEQUENCE public."Склад_id_товара_на_складе_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 I   DROP SEQUENCE public."Склад_id_товара_на_складе_seq";
       public          postgres    false    216            �           0    0 0   Склад_id_товара_на_складе_seq    SEQUENCE OWNED BY     �   ALTER SEQUENCE public."Склад_id_товара_на_складе_seq" OWNED BY public."Склад"."id_товара_на_складе";
          public          postgres    false    238            �           2604    23834    Заказы id_заказа    DEFAULT     �   ALTER TABLE ONLY public."Заказы" ALTER COLUMN "id_заказа" SET DEFAULT nextval('public."Заказы_id_заказа_seq"'::regclass);
 O   ALTER TABLE public."Заказы" ALTER COLUMN "id_заказа" DROP DEFAULT;
       public          postgres    false    219    218            �           2604    23835 C   Изготовляемые лекарства id_лекарства    DEFAULT     �   ALTER TABLE ONLY public."Изготовляемые лекарства" ALTER COLUMN "id_лекарства" SET DEFAULT nextval('public."Изготовляемые лекар_id_лекарства_seq"'::regclass);
 v   ALTER TABLE public."Изготовляемые лекарства" ALTER COLUMN "id_лекарства" DROP DEFAULT;
       public          postgres    false    221    220            �           2604    23836     Клиенты id_клиента    DEFAULT     �   ALTER TABLE ONLY public."Клиенты" ALTER COLUMN "id_клиента" SET DEFAULT nextval('public."Клиенты_id_клиента_seq"'::regclass);
 S   ALTER TABLE public."Клиенты" ALTER COLUMN "id_клиента" DROP DEFAULT;
       public          postgres    false    228    222            �           2604    23837 ,   Компоненты id_компонента    DEFAULT     �   ALTER TABLE ONLY public."Компоненты" ALTER COLUMN "id_компонента" SET DEFAULT nextval('public."Компоненты_id_компонента_seq"'::regclass);
 _   ALTER TABLE public."Компоненты" ALTER COLUMN "id_компонента" DROP DEFAULT;
       public          postgres    false    230    214            �           2604    23838 6   Компоненты id_товара_на_складе    DEFAULT     �   ALTER TABLE ONLY public."Компоненты" ALTER COLUMN "id_товара_на_складе" SET DEFAULT nextval('public."Компоненты_id_товара_на_складе_seq"'::regclass);
 i   ALTER TABLE public."Компоненты" ALTER COLUMN "id_товара_на_складе" DROP DEFAULT;
       public          postgres    false    231    214            �           2604    23839 '   Компоненты стоимость    DEFAULT     �   ALTER TABLE ONLY public."Компоненты" ALTER COLUMN "стоимость" SET DEFAULT nextval('public."Компоненты_стоимость_seq"'::regclass);
 Z   ALTER TABLE public."Компоненты" ALTER COLUMN "стоимость" DROP DEFAULT;
       public          postgres    false    232    214            �           2604    23840 0   Поступление id_поступления    DEFAULT     �   ALTER TABLE ONLY public."Поступление" ALTER COLUMN "id_поступления" SET DEFAULT nextval('public."Поступление_id_поступления_seq"'::regclass);
 c   ALTER TABLE public."Поступление" ALTER COLUMN "id_поступления" DROP DEFAULT;
       public          postgres    false    234    215            �           2604    23841 8   Поступление id_товара_на_складе    DEFAULT     �   ALTER TABLE ONLY public."Поступление" ALTER COLUMN "id_товара_на_складе" SET DEFAULT nextval('public."Поступление_id_товара_на_складе_seq"'::regclass);
 k   ALTER TABLE public."Поступление" ALTER COLUMN "id_товара_на_складе" DROP DEFAULT;
       public          postgres    false    235    215            �           2604    23842     Рецепты id_рецепта    DEFAULT     �   ALTER TABLE ONLY public."Рецепты" ALTER COLUMN "id_рецепта" SET DEFAULT nextval('public."Рецепты_id_рецепта_seq"'::regclass);
 S   ALTER TABLE public."Рецепты" ALTER COLUMN "id_рецепта" DROP DEFAULT;
       public          postgres    false    236    223            �           2604    23843 ,   Склад id_товара_на_складе    DEFAULT     �   ALTER TABLE ONLY public."Склад" ALTER COLUMN "id_товара_на_складе" SET DEFAULT nextval('public."Склад_id_товара_на_складе_seq"'::regclass);
 _   ALTER TABLE public."Склад" ALTER COLUMN "id_товара_на_складе" DROP DEFAULT;
       public          postgres    false    238    216            z          0    23778    Заказы 
   TABLE DATA           �   COPY public."Заказы" ("id_заказа", "id_рецепта", "дата_заказа", "дата_изготовления", "дата_выдачи", "стоимость_заказа") FROM stdin;
    public          postgres    false    218   ��       |          0    23782 -   Изготовляемые лекарства 
   TABLE DATA           �   COPY public."Изготовляемые лекарства" ("id_лекарства", "название", "способ_применения", "способ_приготовления", "стоимость_производства") FROM stdin;
    public          postgres    false    220   ��       ~          0    23786    Клиенты 
   TABLE DATA           �   COPY public."Клиенты" ("id_клиента", "фамилия", "имя", "отчество", "дата_рождения", "адрес", "телефон") FROM stdin;
    public          postgres    false    222   $�       w          0    23764    Компоненты 
   TABLE DATA           �   COPY public."Компоненты" ("id_компонента", "id_товара_на_складе", "название", "форма", "стоимость", "критическая_норма") FROM stdin;
    public          postgres    false    214   ��       x          0    23767    Поступление 
   TABLE DATA           �   COPY public."Поступление" ("id_поступления", "id_товара_на_складе", "количество", "дата_поступления", "дата_истечения_срока_годности") FROM stdin;
    public          postgres    false    215   (�                 0    23789    Рецепты 
   TABLE DATA           �   COPY public."Рецепты" ("id_рецепта", "id_лекарства", "количество", "id_клиента", "ФИО_врача") FROM stdin;
    public          postgres    false    223   ��       y          0    23770 
   Склад 
   TABLE DATA           u   COPY public."Склад" ("id_товара_на_складе", "количество_на_складе") FROM stdin;
    public          postgres    false    216   ��       �          0    23797    Состав 
   TABLE DATA           �   COPY public."Состав" ("id_лекарства", "id_компонента", "количество_компонента") FROM stdin;
    public          postgres    false    225   \�       �           0    0     Заказы_id_заказа_seq    SEQUENCE SET     R   SELECT pg_catalog.setval('public."Заказы_id_заказа_seq"', 171, true);
          public          postgres    false    219            �           0    0 ?   Изготовляемые лекар_id_лекарства_seq    SEQUENCE SET     s   SELECT pg_catalog.setval('public."Изготовляемые лекар_id_лекарства_seq"', 10014, true);
          public          postgres    false    221            �           0    0 $   Клиенты_id_клиента_seq    SEQUENCE SET     U   SELECT pg_catalog.setval('public."Клиенты_id_клиента_seq"', 22, true);
          public          postgres    false    228            �           0    0 0   Компоненты_id_компонента_seq    SEQUENCE SET     c   SELECT pg_catalog.setval('public."Компоненты_id_компонента_seq"', 1050, true);
          public          postgres    false    230            �           0    0 :   Компоненты_id_товара_на_складе_seq    SEQUENCE SET     k   SELECT pg_catalog.setval('public."Компоненты_id_товара_на_складе_seq"', 50, true);
          public          postgres    false    231            �           0    0 +   Компоненты_стоимость_seq    SEQUENCE SET     \   SELECT pg_catalog.setval('public."Компоненты_стоимость_seq"', 1, false);
          public          postgres    false    232            �           0    0 4   Поступление_id_поступления_seq    SEQUENCE SET     f   SELECT pg_catalog.setval('public."Поступление_id_поступления_seq"', 353, true);
          public          postgres    false    234            �           0    0 <   Поступление_id_товара_на_складе_seq    SEQUENCE SET     m   SELECT pg_catalog.setval('public."Поступление_id_товара_на_складе_seq"', 1, false);
          public          postgres    false    235            �           0    0 $   Рецепты_id_рецепта_seq    SEQUENCE SET     U   SELECT pg_catalog.setval('public."Рецепты_id_рецепта_seq"', 61, true);
          public          postgres    false    236            �           0    0 0   Склад_id_товара_на_складе_seq    SEQUENCE SET     a   SELECT pg_catalog.setval('public."Склад_id_товара_на_складе_seq"', 1, false);
          public          postgres    false    238            �           2606    23845    Заказы Заказы_pk 
   CONSTRAINT     m   ALTER TABLE ONLY public."Заказы"
    ADD CONSTRAINT "Заказы_pk" PRIMARY KEY ("id_заказа");
 J   ALTER TABLE ONLY public."Заказы" DROP CONSTRAINT "Заказы_pk";
       public            postgres    false    218            �           2606    23847 ^   Изготовляемые лекарства Изготовляемые лекарства_pk 
   CONSTRAINT     �   ALTER TABLE ONLY public."Изготовляемые лекарства"
    ADD CONSTRAINT "Изготовляемые лекарства_pk" PRIMARY KEY ("id_лекарства");
 �   ALTER TABLE ONLY public."Изготовляемые лекарства" DROP CONSTRAINT "Изготовляемые лекарства_pk";
       public            postgres    false    220            �           2606    23849     Клиенты Клиенты_pk 
   CONSTRAINT     s   ALTER TABLE ONLY public."Клиенты"
    ADD CONSTRAINT "Клиенты_pk" PRIMARY KEY ("id_клиента");
 N   ALTER TABLE ONLY public."Клиенты" DROP CONSTRAINT "Клиенты_pk";
       public            postgres    false    222            �           2606    23851 E   Компоненты Компоненты_id_компонента_key 
   CONSTRAINT     �   ALTER TABLE ONLY public."Компоненты"
    ADD CONSTRAINT "Компоненты_id_компонента_key" UNIQUE ("id_компонента");
 s   ALTER TABLE ONLY public."Компоненты" DROP CONSTRAINT "Компоненты_id_компонента_key";
       public            postgres    false    214            �           2606    23853 O   Компоненты Компоненты_id_товара_на_складе_key 
   CONSTRAINT     �   ALTER TABLE ONLY public."Компоненты"
    ADD CONSTRAINT "Компоненты_id_товара_на_складе_key" UNIQUE ("id_товара_на_складе");
 }   ALTER TABLE ONLY public."Компоненты" DROP CONSTRAINT "Компоненты_id_товара_на_складе_key";
       public            postgres    false    214            �           2606    23855 ,   Компоненты Компоненты_pk 
   CONSTRAINT     �   ALTER TABLE ONLY public."Компоненты"
    ADD CONSTRAINT "Компоненты_pk" PRIMARY KEY ("id_компонента", "id_товара_на_складе");
 Z   ALTER TABLE ONLY public."Компоненты" DROP CONSTRAINT "Компоненты_pk";
       public            postgres    false    214    214            �           2606    23857 0   Поступление Поступление_pk 
   CONSTRAINT     �   ALTER TABLE ONLY public."Поступление"
    ADD CONSTRAINT "Поступление_pk" PRIMARY KEY ("id_поступления");
 ^   ALTER TABLE ONLY public."Поступление" DROP CONSTRAINT "Поступление_pk";
       public            postgres    false    215            �           2606    23859     Рецепты Рецепты_pk 
   CONSTRAINT     s   ALTER TABLE ONLY public."Рецепты"
    ADD CONSTRAINT "Рецепты_pk" PRIMARY KEY ("id_рецепта");
 N   ALTER TABLE ONLY public."Рецепты" DROP CONSTRAINT "Рецепты_pk";
       public            postgres    false    223            �           2606    23861    Склад Склад_pk 
   CONSTRAINT     {   ALTER TABLE ONLY public."Склад"
    ADD CONSTRAINT "Склад_pk" PRIMARY KEY ("id_товара_на_складе");
 F   ALTER TABLE ONLY public."Склад" DROP CONSTRAINT "Склад_pk";
       public            postgres    false    216            �           2620    23862 )   Заказы calculate_order_cost_trigger    TRIGGER     �   CREATE TRIGGER calculate_order_cost_trigger BEFORE INSERT ON public."Заказы" FOR EACH ROW EXECUTE FUNCTION public.calculate_order_cost_trigger();
 D   DROP TRIGGER calculate_order_cost_trigger ON public."Заказы";
       public          postgres    false    218    241            �           2620    23863 4   Поступление check_expiration_date_trigger    TRIGGER     �   CREATE TRIGGER check_expiration_date_trigger BEFORE INSERT OR UPDATE ON public."Поступление" FOR EACH ROW EXECUTE FUNCTION public.check_expiration_date();
 O   DROP TRIGGER check_expiration_date_trigger ON public."Поступление";
       public          postgres    false    255    215            �           2620    23864 &   Склад component_threshold_trigger    TRIGGER     �   CREATE TRIGGER component_threshold_trigger AFTER UPDATE ON public."Склад" FOR EACH ROW EXECUTE FUNCTION public.check_component_threshold();
 A   DROP TRIGGER component_threshold_trigger ON public."Склад";
       public          postgres    false    254    216            �           2620    23865 "   Заказы update_orders_trigger    TRIGGER     �   CREATE TRIGGER update_orders_trigger AFTER INSERT ON public."Заказы" FOR EACH ROW EXECUTE FUNCTION public.update_orders_trigger();
 =   DROP TRIGGER update_orders_trigger ON public."Заказы";
       public          postgres    false    256    218            �           2606    23866    Заказы Заказы_fk0    FK CONSTRAINT     �   ALTER TABLE ONLY public."Заказы"
    ADD CONSTRAINT "Заказы_fk0" FOREIGN KEY ("id_рецепта") REFERENCES public."Рецепты"("id_рецепта");
 K   ALTER TABLE ONLY public."Заказы" DROP CONSTRAINT "Заказы_fk0";
       public          postgres    false    218    3285    223            �           2606    23871 1   Поступление Поступление_fk0    FK CONSTRAINT     �   ALTER TABLE ONLY public."Поступление"
    ADD CONSTRAINT "Поступление_fk0" FOREIGN KEY ("id_товара_на_складе") REFERENCES public."Склад"("id_товара_на_складе");
 _   ALTER TABLE ONLY public."Поступление" DROP CONSTRAINT "Поступление_fk0";
       public          postgres    false    3277    215    216            �           2606    23876 !   Рецепты Рецепты_fk0    FK CONSTRAINT     �   ALTER TABLE ONLY public."Рецепты"
    ADD CONSTRAINT "Рецепты_fk0" FOREIGN KEY ("id_лекарства") REFERENCES public."Изготовляемые лекарства"("id_лекарства");
 O   ALTER TABLE ONLY public."Рецепты" DROP CONSTRAINT "Рецепты_fk0";
       public          postgres    false    220    3281    223            �           2606    23881 !   Рецепты Рецепты_fk1    FK CONSTRAINT     �   ALTER TABLE ONLY public."Рецепты"
    ADD CONSTRAINT "Рецепты_fk1" FOREIGN KEY ("id_клиента") REFERENCES public."Клиенты"("id_клиента");
 O   ALTER TABLE ONLY public."Рецепты" DROP CONSTRAINT "Рецепты_fk1";
       public          postgres    false    222    3283    223            �           2606    23886    Склад Склад_fk0    FK CONSTRAINT     �   ALTER TABLE ONLY public."Склад"
    ADD CONSTRAINT "Склад_fk0" FOREIGN KEY ("id_товара_на_складе") REFERENCES public."Компоненты"("id_товара_на_складе");
 G   ALTER TABLE ONLY public."Склад" DROP CONSTRAINT "Склад_fk0";
       public          postgres    false    3271    216    214            �           2606    23891    Состав Состав_fk0    FK CONSTRAINT     �   ALTER TABLE ONLY public."Состав"
    ADD CONSTRAINT "Состав_fk0" FOREIGN KEY ("id_лекарства") REFERENCES public."Изготовляемые лекарства"("id_лекарства");
 K   ALTER TABLE ONLY public."Состав" DROP CONSTRAINT "Состав_fk0";
       public          postgres    false    220    225    3281            �           2606    23896    Состав Состав_fk1    FK CONSTRAINT     �   ALTER TABLE ONLY public."Состав"
    ADD CONSTRAINT "Состав_fk1" FOREIGN KEY ("id_компонента") REFERENCES public."Компоненты"("id_компонента");
 K   ALTER TABLE ONLY public."Состав" DROP CONSTRAINT "Состав_fk1";
       public          postgres    false    225    214    3269            z   �  x���Qr� D��.��	�DO�����i�l#ڙ|h�VX�$RC	�($� ��񡒢��OR[�5��ȁ��V�%����\�=ҒK�rI�H/O���s�bb͒��6��)� v�v0�`��}$>�>j�?t}��#X$���dB�a>�YO4�斤i'm	`�J���lE�?�rU���6p��бd}�y<L>>�d>3�,Z$�l-3�Y	�|F����J�()����`�~��~���L�� -��c.v݋:2�M��ོ���\6ه�n��[�n�뚾5w��4w�4�oPv]����ޯ�փT$�J��Q�q�t�p4K��Xj�$}��Q�n*|�Bl,��hx\�o��O�-,�6�k��O����5ͻh!�M�����~�+�iD��ȿy2���j�?4�S�&0���o��-�n�ϰ���T��d����7p��t      |   �  x�ՔMN�0���)r ����]8L�VhQY�@B!q ���(I�+<߈7��*��YDr�7ߌgl�,�/a&h�;�Wx����
K�������\��eʳ2LQ`�S.|��s{�&y�#���W�=W�)�RF�\K0z8����t�\5(i:��Y	g����g�LIS�k�(��B/��7x�]��Vo�P��)c
�G�8l),u�����[V��F��Bɖ�	^��ڏ�eh�R��0�ĉ������ĞPhu��c��O���"���Q���7��;�\��$��[J��������^^��n%�<�&�͐�$.ɪέ��s��}>V|�qL��Խ#��:��'/L��
�uXɹ	͆���}M+-��L���i�؃�/Ƶ���y�$�Ad      ~   o  x�}UmR�0�-���ɲc�.=L�:3���t�6��w�$��^A�Q߮�	-��1�J�ݷk#�W����_v��V��>&ϵ�_�o}U�'��D���D�Ɨ��ை�0�M�i�rm��k���C��(�V�K�>�G�~+�)�
�P�K��C}��U��s�1E=cjE=���H�V&Dc��g���n�1�bȉT�*�er甶*�o�J�7���"���I��_����D�����kl<������-�#}+�(��� �N8	j�yw�bXJ��)�SJj�,w�S�������U�@�ј'W���r���M������E{^=jLE�?��jÉ��UymjN�k��;A�˔�*S�^Q2���ǣ�]�3ѣg���8�M��s*V�8�v�>Q:Q�~����j'z'srϪ�t_����}5]�4L�R�9��Z.����r�#�Ҡ(׈{�^Y���Ư��p�$��*�)��io9�hZ-zL-����Ӱk��Y�0�Y
Y�x�16�Y�0��a�bc��XKb������?`	v~Kf�Ѧ�ŌZ5>=�:o6�N�8�I��i�Z|���T4K@��N�Զ�m[��P霠���)���Yh��!qo	�����z�1U7�P:�۠iНcM��Rl{t�),�Nm����4��@w撧Dh��8L G�тsa���I҆�X�&g�(��/i��ijQW$�*�㦭Z
��	Q�Wۄ��m�L�q�r���a:��,P�6�$ͳ~y<7�D�����A3h�jTp�>��FV�s��T�m3MQϟX����.�I��%8�'Y�Q���4��i��&�q<�9�_��yѣ-qܾͣ����?Pt`��w ���s~�      w   u  x��V[n�P���"+@��_����@�>�Ҫ��䶱b����xG��;��\�#���y��8i�d������q��?s��q<�~|MuB�,MG��+^���;�3�������/��
�Z<^sGYBNsʉ�$4Ҝ�e'Fr#O`�7㛧i��*�.��W�r����[M"q֚��4����Q7��T��J*V-�6b;�%����]WWP.�U��w}wp��#������n�<�!j��!@�>ߊ=����l��2�Rl� ��IX)�(u��n���>iB ����V�ay��_+'M	�/0�F�ǞXmm%���)*�1# �����{�?��,�#�?�*؊����Bi9(��\k?�dA��L�80����(g���XӒ �.��Ҍ짜�XҊ ���2!�56�Bi����L�� Lf���.�/t�{m��Ә���R�� >S�,u��Ģ�2�2���#\dY[EO�&��� �[^�331�,'@ͷ�ĥ�;y�����N���o��L�YI ����F�Sg�T@�Ϗn�C�0�� [�=]�nӔ.P��x�5
�w*4*ua��r�Ls��	���͸� ��Ά�m�~��伯p�me]F *k�e������7>��[�N��� �]]���o�*E��ZEp�,�1'�>W��Z+?zz`���+e�"W�4�i�e�d�& ��	�8�nA ������e��y�:�R��Kd��!L&p�e��<^��]CW����M�m?w6sG@0G�����)�H��r��E��HNol��@r$),�6�9���K�B��ꡌ/��R�?U�br�#��7fj��z#���Y��Tڭ����K3���Uf[�R�_�^���o�)j�;�?U�ڿ|1������q      x   �  x���Q�� E����ǒ���t������iȜ�����	+�PQ���]�׺l�ˇ�	��;�n4� �&`I܉;p�W�I<�Sr�\���֥�+մԆ@{SMKm
�SM����%���pK���F9�\��-8���.]���QϠ�M�����/�6��O?+��}N?/�.����}�������|J%�I�����ps�p]��7����^ච��O��}�$��¯��� ���_,y�+���rMN?���__�0?����X����g�7��d>F?�߸į=���o�TE����o��q��ƪ�����_����;�x�����U�����7V}G��>�w}c�wt�ϯ����!>�O����;�������U�yI�v?�_�w�4��1�U}�I���`}c�w�4���~U߉��v?�_�w��[~F���Li���~U�٥m�%�v��=����M6�\�{Ni�����u������d�Kp,'��ԯ����~����󈣾������d������|~�8h��V�g?�	�^'N`4~��n��y��>0���O��_��)���v�µNM�&G��ku^��A��hY����Q��#���n+:=F�+�|��0�vu�����G�f?�~��U�;�8VY�-�m;�f��	��}x��=a�~���%~9��_�-��x����S{���x<��'�         �  x��S[N�0�vN��<ꤹ�I#��Tj) � P?�m#�Wΰ��'�$��מ��ٍ�|��|*_�-)�U����/ީ0)�����,T�
��8��\�XQeR3riN%m�!)K3tBJ�y������3#$�r*�5R�w*�ܓ=��=#����Y�347 9Wë���[Ya����dRfY�<�iA[$bG����U�甫�+h�Y�:b'p;V4c���c.*r�fƗ|��������k�{q*�6�I���GP��M3ٔ�߭�Q�{��/;�h!�U��7�-��i��q�<7o:�;uL����!�l��n6���ttԒ���uank�xc[h ^4�C|�n[��IwR�}�Ҿ5�U�<��p���L{��P'vȡ8�g,�q�5�{j�f���7rhE��!�*�i����8?e9`=      y   �   x����E1Ϧ�UN���ￎ5� F`*x�u"?|>���m�d+1p���P��,�
-d�M�6F���3�P��$�>�>6�:$��s��yѼ�T�T{^^�+��4Yt[�z�b�b����;^?A�tۍ}�{5�`�����?m.*N      �   �   x�e��� �o(f�#�l�ul�L,K����1��hS֕��F"a��H�Şg�o��<a�T���YM��ae`@E�ٜ6��=�V*X�`���1���n�e��\��4������ ����yc�<���� �<B     