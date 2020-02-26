passcode_type_query = """
    select
    date(daysSince1970*86400, 'unixepoch', 'utc') as day,
    key,
    value,
    case
            when value = -1 then '6 digit'
            when value = 0 then 'No passcode'
            when value = 1 then '4 digit'
            when value = 2 then 'Custom alphanumeric'
            when value = 3 then 'Custom numeric'
            else value 
            END as passcodeType
    from Scalars
    where key = 'com.apple.passcode.PasscodeType'
    """

passcode_success_fail_query = """
    select 
    date(daysSince1970*86400, 'unixepoch', 'utc') as day,
    key, value
    from Scalars
    where key like 'com.apple.passcode.NumPasscode%'
    """

passcode_finger_template_query = """
    SELECT
    DATE(DAYSSINCE1970*86400, 'unixepoch') AS DAY,
    KEY AS "KEY",
    VALUE AS "VALUE"
    FROM
    SCALARS
    where key = 'com.apple.fingerprintMain.templateCount'
    """

scalars_query = """
    SELECT
           DATE(DAYSSINCE1970*86400, 'unixepoch') AS DAY,
               KEY AS "KEY",
               VALUE AS "VALUE"
            FROM
               SCALARS
    """

distribution_keys_query = """
    SELECT
                    DATE(DISTRIBUTIONKEYS.DAYSSINCE1970*86400, 'unixepoch') AS "DAY",
                    DISTRIBUTIONVALUES.SECONDSINDAYOFFSET AS "SECONDS IN DAY OFFSET",
                    DISTRIBUTIONKEYS.KEY AS "KEY",
                    DISTRIBUTIONVALUES.VALUE AS "VALUE",
                    DISTRIBUTIONVALUES.DISTRIBUTIONID AS "DISTRIBUTIONVALUES TABLE ID"
            FROM
                    DISTRIBUTIONKEYS 
                    LEFT JOIN
                            DISTRIBUTIONVALUES 
                            ON DISTRIBUTIONKEYS.ROWID = DISTRIBUTIONVALUES.DISTRIBUTIONID
    """
