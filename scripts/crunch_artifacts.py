import typing
from .artifact_loader import ArtifactSpec


def crunch_artifacts(
        plugins: typing.Sequence[ArtifactSpec], extracttype, input_path, out_params, wrap_text,
        loader: plugin_loader.PluginLoader, casedata, time_offset, profile_filename, itunes_backup_password=None, decryption_keys=None):
    start = process_time()
    start_wall = perf_counter()

    logfunc('Processing started. Please wait. This may take a few minutes...')

    logfunc('\n--------------------------------------------------------------------------------------')
    logfunc(f'iLEAPP v{leapp_version}: iOS Logs, Events, And Plists Parser')
    logfunc('Objective: Triage iOS Full File System and iTunes Backup Extractions.')
    logfunc('By: Alexis Brignoni | @AlexisBrignoni | abrignoni.com')
    logfunc('By: Yogesh Khatri   | @SwiftForensics | swiftforensics.com\n')
    logdevinfo()
    seeker = None
    password = itunes_backup_password
    try:
        if extracttype == 'fs':
            seeker = FileSeekerDir(input_path, out_params.data_folder)

        elif extracttype == 'file':
            seeker = FileSeekerFile(input_path, out_params.data_folder)

        elif extracttype in ('tar', 'gz'):
            seeker = FileSeekerTar(input_path, out_params.data_folder)

        elif extracttype == 'zip':
            seeker = FileSeekerZip(input_path, out_params.data_folder)

        elif extracttype == 'itunes':
            itunes_backup_type = get_itunes_backup_type(input_path)
            if itunes_backup_type:
                supported, encrypted, message = check_itunes_backup_status(
                    input_path, itunes_backup_type)
                if not supported:
                    logfunc(message)
                    return False
                else:
                    if encrypted:
                        while not decryption_keys:
                            if not password:
                                password = getpass("iTunes Backup password: ")
                            decryption_keys, _ = decrypt_itunes_backup(input_path, password)
                            if not decryption_keys:
                                return False
            else:
                logfunc('Input folder is not a valid iTunes backup!')
                return False
            seeker = FileSeekerItunes(input_path, out_params.data_folder,
                                    itunes_backup_type, decryption_keys)

        else:
            logfunc('Error on argument -o (input type)')
            return False
    except Exception as ex:
        logfunc('Had an exception in Seeker - see details below. Terminating Program!')
        temp_file = io.StringIO()
        traceback.print_exc(file=temp_file)
        logfunc(temp_file.getvalue())
        temp_file.close()
        return False

    # Now ready to run
    # add last_build at the start except for iTunes backups
    if extracttype != 'itunes':
        plugins.insert(0, loader["last_build"])

    logfunc(f'Info: {len(loader) - 2} modules loaded.') # excluding last_build and iTunesBackupInfo
    if profile_filename:
        logfunc(f'Loaded profile: {profile_filename}')
    logfunc(f'Artifact to parse: {len(plugins)}')
    logfunc(f'File/Directory selected: {input_path}')
    logfunc('\n--------------------------------------------------------------------------------------')

    log = open(os.path.join(out_params.output_folder_base, '_HTML', '_Script_Logs', 'ProcessedFilesLog.html'), 'w+', encoding='utf8')
    log.write(f'Extraction/Path selected: {input_path}<br><br>')
    log.write(f'Timezone selected: {time_offset}<br><br>')

    # Special processing for iTunesBackup Info.plist as it is a seperate entity, not part of the Manifest.db. Seeker won't find it
    if extracttype == 'itunes':
        info_plist_path = os.path.join(input_path, 'Info.plist')
        if os.path.exists(info_plist_path):
            # process_artifact([info_plist_path], 'iTunesBackupInfo', 'Device Info', seeker, out_params.output_folder_base)
            #plugin.method([info_plist_path], out_params.output_folder_base, seeker, wrap_text)
            report_folder = os.path.join(out_params.output_folder_base, '_HTML', 'iTunes Backup')
            if not os.path.exists(report_folder):
                try:
                    os.makedirs(report_folder)
                except (FileExistsError, FileNotFoundError) as ex:
                    logfunc('Error creating report directory at path {}'.format(report_folder))
                    logfunc('Error was {}'.format(str(ex)))
            loader["itunes_backup_info"].method([info_plist_path], report_folder, seeker, wrap_text, time_offset)
            report_folder = os.path.join(out_params.output_folder_base, '_HTML', 'Installed Apps')
            if not os.path.exists(report_folder):
                try:
                    os.makedirs(report_folder)
                except (FileExistsError, FileNotFoundError) as ex:
                    logfunc('Error creating report directory at path {}'.format(report_folder))
                    logfunc('Error was {}'.format(str(ex)))
            loader["itunes_backup_installed_applications"].method([info_plist_path], report_folder, seeker, wrap_text, time_offset)
            #del search_list['last_build'] # removing last_build as this takes its place
            print([info_plist_path])  # TODO Remove special consideration for itunes? Merge into main search
        else:
            logfunc('Info.plist not found for iTunes Backup!')
            log.write('Info.plist not found for iTunes Backup!')

    # Search for the files per the arguments
    parsed_modules = 0
    lava_only = False
    artifact_search_pattern_id = 0
    file_path_ids = set()

    for plugin_number, plugin in enumerate(plugins, start=1):
        logfunc()
        logfunc('[{}/{}] {} [{}] artifact started'.format(plugin_number, len(plugins),
                                                              plugin.name, plugin.module_name))
        output_types = plugin.artifact_info.get('output_types', '')
        if isinstance(plugin.search, list) or isinstance(plugin.search, tuple):
            search_regexes = plugin.search
        elif plugin.search is None:
            search_regexes = plugin.search
        else:
            search_regexes = [plugin.search]
        files_found = []
        log.write(f'<b>For {plugin.name} module</b>')
        if search_regexes is None:
            log.write(f'<ul><li>No search regexes provided for {plugin.name} module.')
            log.write("<ul><li><i>'_lava_artifacts.db'</i> used as source file.</li></ul></li></ul>")
            files_found = [os.path.join(out_params.output_folder_base, '_lava_artifacts.db')]
        else:
            for artifact_search_regex in search_regexes:
                artifact_search_pattern_id += 1
                lava_insert_sqlite_artifact_search_pattern(
                    artifact_search_pattern_id, plugin.module_name, plugin.name, artifact_search_regex)
                pattern_already_searched = artifact_search_regex in seeker.searched
                found = seeker.search(artifact_search_regex)
                if not found:
                    if plugin.name == 'logarchive' and extracttype != 'fs' and extracttype != 'file':
                        src = os.path.join(os.path.dirname(input_path), "logarchive.json")
                        dst = os.path.join(out_params.data_folder, "logarchive.json")
                        if os.path.exists(src):
                            copy2(src, dst)
                            files_found.append(dst)
                    log.write(f'<ul><li>No file found for regex <i>{artifact_search_regex}</i></li></ul>')
                else:
                    log.write(f'<ul><li>{len(found)} {"files" if len(found) > 1 else "file"} for regex <i>{artifact_search_regex}</i> located at:')
                    for pathh in found:
                        if pathh.startswith('\\\\?\\'):
                            pathh = pathh[4:]
                        log.write(f'<ul><li>{pathh}</li></ul>')
                        if seeker.file_infos.get(pathh):
                            file_path_id = id(seeker.file_infos.get(pathh))
                            if not pattern_already_searched and file_path_id not in file_path_ids:
                                lava_insert_sqlite_file_path(file_path_id,seeker.file_infos.get(pathh).source_path)
                                file_path_ids.add(file_path_id)
                            lava_insert_sqlite_artifact_link_pattern_to_file(artifact_search_pattern_id, file_path_id)
                    log.write(f'</li></ul>')
                    files_found.extend(found)
        if files_found:
            if not lava_only and 'lava_only' in output_types:
                lava_only = True
            category_folder = os.path.join(out_params.output_folder_base, '_HTML', plugin.category)
            if not os.path.exists(category_folder):
                try:
                    os.makedirs(category_folder)
                except (FileExistsError, FileNotFoundError) as ex:
                    logfunc('Error creating {} report directory at path {}'.format(plugin.name, category_folder))
                    logfunc('Error was {}'.format(str(ex)))
                    continue  # cannot do work
            try:
                plugin.method(files_found, category_folder, seeker, wrap_text, time_offset)
                if plugin.name == 'logarchive':
                    lava_db_path = os.path.join(out_params.output_folder_base, '_lava_artifacts.db')
                    if does_table_exist_in_db(lava_db_path, 'logarchive'):
                        loader["logarchive_artifacts"].method([lava_db_path], category_folder, seeker, wrap_text, time_offset)
                    if does_table_exist_in_db(lava_db_path, 'logarchive_artifacts'):
                        unifed_logs_artifacts = []
                        unifed_logs_artifacts = [plugin.name for plugin in loader.plugins
                                                 if plugin.module_name=='logarchive'
                                                 and plugin.name != 'logarchive'
                                                 and plugin.name != 'logarchive_artifacts']
                        for unifed_log_artifact in unifed_logs_artifacts:
                            loader[unifed_log_artifact].method([lava_db_path], category_folder, seeker, wrap_text, time_offset)
            except Exception as ex:
                logfunc('Reading {} artifact had errors!'.format(plugin.name))
                logfunc('Error was {}'.format(str(ex)))
                logfunc('Exception Traceback: {}'.format(traceback.format_exc()))
                continue  # nope
        else:
            logfunc(f"No file found")
        logfunc('{} [{}] artifact completed'.format(plugin.name, plugin.module_name))
        parsed_modules += 1
        GuiWindow.set_progress_bar(parsed_modules, len(plugins))
        log.flush()
    log.close()

    write_device_info()
    if lava_only:
        write_lava_only_log()
    logfunc('')
    logfunc('Processes completed.')
    end = process_time()
    end_wall = perf_counter()
    run_time_secs =  end - start
    run_time_HMS = strftime('%H:%M:%S', gmtime(run_time_secs))
    logfunc("Processing time = {}".format(run_time_HMS))
    run_time_secs =  end_wall - start_wall
    run_time_HMS = strftime('%H:%M:%S', gmtime(run_time_secs))
    logfunc("Processing time (wall)= {}".format(run_time_HMS))

    logfunc('')
    logfunc('Report generation started.')
    # remove the \\?\ prefix we added to input and output paths, so it does not reflect in report
    if is_platform_windows():
        if out_params.output_folder_base.startswith('\\\\?\\'):
            out_params.output_folder_base = out_params.output_folder_base[4:]
        if input_path.startswith('\\\\?\\'):
            input_path = input_path[4:]

    report.generate_report(out_params.output_folder_base, run_time_secs, run_time_HMS, extracttype, input_path, casedata, profile_filename, icons, lava_only)
    logfunc('Report generation Completed.')
    logfunc('')
    logfunc(f'Report location: {out_params.output_folder_base}')

    return True
