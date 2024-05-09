-- PROCEDURE: public.update_survival_data()
-- Description:
-- This procedure generates a dataset for survival analysis by extracting relevant data from various
-- tables in the database and populating the 'survival_data' table.

CREATE OR REPLACE PROCEDURE public.update_survival_data(
	)
LANGUAGE 'plpgsql'
AS $BODY$

DECLARE
    row_count INT;
BEGIN
    -- Log message for truncation
    RAISE NOTICE 'Truncating survival_data table...';
    
    -- Truncate the survival_data table
    TRUNCATE TABLE survival_data;
    
    -- Log message for truncation completion
    RAISE NOTICE 'Survival_data table truncated.';

    -- Insert data into survival_data table
    INSERT INTO survival_data (cliid, app_id, ap_date, close_date, contractperiod, paidamount, initialamount, exp_int, riskclass, serveddays, ficoscore, npaidcount, naplcount, n_dpds, max_dpd, age, gender, n_salary, n_vehicles, n_dahk, sum_dahk, n_dependents, been_married, mobile_operator, marz, tenure, event) --email_extension
    WITH max_ap_date AS (
        SELECT MAX(ap_date) AS max_date FROM consumer_main
    ), 
    last_ap_per_client AS (
        SELECT 
            cliid,
            app_id AS last_app_id
        FROM (
            SELECT 
                cliid,
                app_id,
                ROW_NUMBER() OVER (PARTITION BY cliid ORDER BY ap_date DESC) AS rn
            FROM consumer_main 
            WHERE EXTRACT(year FROM ap_date) = 2021
        ) ranked
        WHERE rn = 1
    ), 
    base AS (
        SELECT 
            CM.cliid,
            CM.app_id,
            CM.ap_date,
            close_date,
            contractperiod,
            paidamount,
            initialamount,
            exp_int,
			riskclass,
            EXTRACT(day FROM (close_date - ap_date)) AS serveddays,
            ficoscore,
            npaidcount,
            naplcount,
            n_dpds,
            max_dpd,
            CAST(EXTRACT('YEAR' FROM age(CM.ap_date, CC.birth_date)) AS INT) AS age, 
            gender,
            n_salary,
            CASE
                WHEN n_vehicles IS NULL THEN 0
                ELSE CAST(n_vehicles as INT)
            END AS n_vehicles,
			CASE
                WHEN n_dahk IS NULL THEN 0
                ELSE CAST(n_dahk as INT)
            END AS n_dahk,
			CASE
                WHEN sum_dahk IS NULL THEN 0
                ELSE sum_dahk
            END AS sum_dahk,
            CASE
                WHEN n_dependents IS NULL THEN 0
                ELSE CAST(n_dependents as INT)
            END AS n_dependents,
            CASE
                WHEN been_married IS NULL THEN 0
                ELSE 1
            END AS been_married,
            mobile_operator,
            -- SUBSTRING(CC.email FROM POSITION('@' IN email) + 1) AS email_extension,
            marz, 
            CASE 
                WHEN (LEAD(CM.ap_date) OVER (PARTITION BY CM.cliid ORDER BY CM.ap_date) IS NOT NULL) THEN EXTRACT(day FROM LEAD(CM.ap_date) OVER (PARTITION BY CM.cliid ORDER BY CM.ap_date) - HC_new.close_date)
                ELSE EXTRACT(day FROM (SELECT max_date FROM max_ap_date) - HC_new.close_date)
            END AS tenure, 
            CASE 
                WHEN (LEAD(CM.ap_date) OVER (PARTITION BY CM.cliid ORDER BY CM.ap_date) IS NULL) THEN FALSE
                ELSE TRUE
            END AS event
        FROM consumer_main CM 
        LEFT JOIN consumer_client CC ON CM.cliid = CC.cliid
        LEFT JOIN marz AS M ON M.marz_id = CC.marz_id
        LEFT JOIN consumer_hc AS hc_new ON hc_new.app_id = CM.app_id
        LEFT JOIN (
            SELECT app_id, count(reg_num) AS n_vehicles
            FROM eceng_vehicle_info EVI
            GROUP BY app_id
        ) EVI ON EVI.app_id = CM.app_id
	    LEFT JOIN (
            SELECT app_id, count(app_id) AS n_dahk, sum(recoversum) AS sum_dahk
            FROM eceng_ces_data ECD
            GROUP BY app_id
        ) ECD ON ECD.app_id = CM.app_id
        LEFT JOIN (
            SELECT cliid, count(relation) AS n_dependents
            FROM consumer_family_members CFM
            WHERE relation = 3
            GROUP BY cliid
        ) CFM3 ON CFM3.cliid = CC.cliid
        LEFT JOIN (
            SELECT cliid, count(relation) AS been_married
            FROM consumer_family_members CFM
            WHERE relation = 5
            GROUP BY cliid
        ) CFM5 ON CFM5.cliid = CC.cliid
        ORDER BY CM.cliid, CM.ap_date
    )
		
    SELECT B.*
    FROM base B
    LEFT JOIN consumer_main CM ON B.app_id = CM.app_id
    JOIN last_ap_per_client LA ON B.app_id = LA.last_app_id
    WHERE CM.apl_stage = 28 -- closed loans
    AND tenure >= 0; -- multiple CashMe loans are prohibited

    -- Log message for insertion
    GET DIAGNOSTICS row_count = ROW_COUNT;
    RAISE NOTICE '% rows inserted into survival_data table.', row_count;

END;
$BODY$;
