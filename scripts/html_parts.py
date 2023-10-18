# Variables in page_header = {title}
# 
page_header = \
"""<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <meta http-equiv="x-ua-compatible" content="ie=edge">
        <title>{0}</title>
        <!-- Dark mode -->
        <link rel="stylesheet" href="_elements/dark-mode.css">
        <!-- Font Awesome -->
        <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.11.2/css/all.css">
        <!-- Google Fonts Roboto -->
        <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap">
        <!-- Bootstrap core CSS -->
        <link rel="stylesheet" href="_elements/MDB-Free_4.13.0/css/bootstrap.min.css">
        <!-- Material Design Bootstrap - TOGGLE THIS FOR ALTERNATE DESIGN!-->
        <link rel="stylesheet" href="_elements/MDB-Free_4.13.0/css/mdb.min.css">
        <!-- Your custom styles (optional) -->
        <link rel="stylesheet" href="_elements/dashboard.css">
        <link rel="stylesheet" href="_elements/chats.css">
        
        <!-- MDBootstrap Datatables  -->
        <link rel="stylesheet" href="_elements/MDB-Free_4.13.0/css/addons/datatables.min.css" rel="stylesheet">

        <!-- Icons -->
        <!--script src="https://unpkg.com/feather-icons/dist/feather.min.js"></script-->
        <script src="_elements/feather.min.js"></script>
    </head>
    <body>
"""
# body_part_1 includes fixed navbar at top and starting tags for rest of page
# Variables = {version_info}
body_start = \
"""
    <!-- Start your project here-->
    <nav class="navbar navbar-dark fixed-top bg-dark flex-md-nowrap p-0 shadow">
        <a class="navbar-brand col-sm-3 col-md-2 mr-0" href="#">{0}</a>
        <div class="custom-control custom-switch">
            <input type="checkbox" class="custom-control-input" id="darkSwitch" />
            <label class="custom-control-label mr-2" for="darkSwitch" style="color:white">Dark Switch</label>
        </div>
        <script src="_elements/dark-mode-switch.js"></script>
    </nav>

    <div class="container-fluid">
        <div class="row">
"""
body_sidebar_setup = \
"""
            <nav class="col-md-2 d-none d-md-block bg-light sidebar">
                <div class="sidebar-sticky" id="sidebar_id">
                    <ul class="nav flex-column">
"""
# The 'active' class must be set only for the current page, it will highlight that entry in blue
#   class="nav-link active"
# Below is sample data, use own generated data!
body_sidebar_dynamic_data = \
"""
                        <h6 class="sidebar-heading justify-content-between align-items-center px-3 mt-4 mb-1 text-muted">
                            Saved reports
                        </h6>
                        <li class="nav-item">
                            <a class="nav-link" href="#">
                                <span data-feather="home"></span> Report Home
                            </a>
                        </li>
                        <h6 class="sidebar-heading justify-content-between align-items-center px-3 mt-4 mb-1 text-muted">
                            Recent Activity
                        </h6>
                        <li class="nav-item">
                            <a class="nav-link" href="#">
                                <span data-feather="activity"></span> RecentActivity_0
                            </a>
                        </li>
                        <h6 class="sidebar-heading justify-content-between align-items-center px-3 mt-4 mb-1 text-muted">
                            Script Logs
                        </h6>
                        <li class="nav-item">
                            <a class="nav-link" href="#">
                                <span data-feather="archive"></span> Processed Files Log
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#">
                                <span data-feather="archive"></span> Screen Output
                            </a>
                        </li>
                        <h6 class="sidebar-heading justify-content-between align-items-center px-3 mt-4 mb-1 text-muted">
                            Usage Stats
                        </h6>
                        <li class="nav-item">
                            <a class="nav-link" href="#">
                                <span data-feather="bar-chart-2"></span> UsageStats_0
                            </a>
                        </li>
                        <h6 class="sidebar-heading justify-content-between align-items-center px-3 mt-4 mb-1 text-muted">
                            Wellbeing
                        </h6>
                        <li class="nav-item">
                            <a class="nav-link" href="#">
                                <span data-feather="layers"></span> Events
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#">
                                <span data-feather="user"></span> Wellbeing Account
                            </a>
                        </li>
"""
body_sidebar_dynamic_data_placeholder = '<!--__INSERT-NAV-BAR-DATA-HERE__-->'
body_sidebar_trailer = \
"""
                    </ul>
                    <br /><br />
                </div>
            </nav>
"""

body_main_header = \
"""
            <main role="main" class="col-md-9 ml-sm-auto col-lg-10 px-4">
"""
# Variable {title}, {description}
body_main_data_title = \
"""
                <div class="justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
                    <h1 class="display-5">{0}</h1>
                    <h6 class="animated fadeIn mb-3">{1}</h6>
                </div>
"""
body_spinner = \
"""
                <div id="mySpinner" class="spinner-border text-info float-right" role="status">
                    <span class="sr-only">Loading...</span>
                </div>
"""
body_infinite_loading_bar = \
"""
                <div id ="infiniteLoading" class="progress md-progress primary-color-dark">
                    <div class="indeterminate"></div>
                </div>
"""
# body_main_data is a placeholder, replace content with real data
body_main_data = \
"""
                <h5>All dates and times are in UTC unless stated otherwise.</h5>
                <div class="alert alert-warning" role="alert">
                    All dates and times are in UTC unless noted otherwise!
                </div>
                <p class="note note-primary mb-4">
                    All dates and times are in UTC unless noted otherwise!
                </p>
                <h2>Case</h2>
                <div class="table-responsive">
                    <table class="table table-bordered table-hover table-sm" width="70%">
                        <tbody>
                            <tr>
                                <td>Extraction Location</td>
                                <td>N:\aleapp_images\Pixel 5</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div class="androidevents">
                    <h1>Android Events</h1>
                    <h1>Android Events</h1>
                </div>
"""
# tabs code for Case information in index.html
# Variables are {case_table_code}, {script_run_log}, {processed_file_list}
tabs_code = \
"""
    <ul class="nav nav-tabs" id="myTab" role="tablist">
        <li class="nav-item">
            <a class="nav-link active" id="case-tab" data-toggle="tab" href="#case" role="tab" aria-controls="case" aria-selected="true">Details</a>
        </li>
        <li class="nav-item">
            <a class="nav-link" id="device-list-tab" data-toggle="tab" href="#device" role="tab" aria-controls="device" aria-selected="false">Device details</a>
        </li>
        <li class="nav-item">
            <a class="nav-link" id="run-log-tab" data-toggle="tab" href="#run" role="tab" aria-controls="run" aria-selected="false">Script run log</a>
        </li>
        <li class="nav-item">
            <a class="nav-link" id="files-list-tab" data-toggle="tab" href="#files" role="tab" aria-controls="files" aria-selected="false">Processed files list</a>
        </li>
    </ul>
    <div class="tab-content" id="myTabContent">
        <div class="tab-pane fade show active" id="case" role="tabpanel" aria-labelledby="case-tab"><br />{}</div>
        <div class="tab-pane fade" id="device" role="tabpanel" aria-labelledby="device-tab"><br />{}</div>
        <div class="tab-pane fade text-monospace" id="run" role="tabpanel" aria-labelledby="script-run-tab"><br />{}</div>
        <div class="tab-pane fade" id="files" role="tabpanel" aria-labelledby="profile-tab"><br />{}</div>
    </div>
"""
# thank you note , at bottom of index.html
thank_you_note = \
"""
                <br /><br /><br />
                <div class="text-center">
                    <br />
                    <div class="card bg-white mb-3" style="max-width: 500px; margin:auto">
                        <div class="row no-gutters">
                            <center><div class="col-md-4">
                                <img src="_elements/logo.jpg" class="card-img" alt="DFIR">
                            </div>
                            <div class="col-md-8">
                            <div class="card-body">
                                <h5 class="card-title">Thank you for using iLEAPP</h5>
                                <p class="card-text">
                                    Support open source and report any bugs!
                                </p>
                                <!--Github-->
                                <a class="btn-floating btn-git" type="button" role="button" href="https://github.com/abrignoni/ileapp" target="_blank"><i class="fab fa-github"></i> Project Home </a>
                                <p class="card-text fadeIn"><small class="text-muted">iLEAPP Team</small></p>
                            </div>
                            </div></center>
                        </div>
                    </div>
                    <br />
                    <br />
                </div><!--end text-center area-->
"""

# Variable: HTML List of individual contributors (for index.html)
credits_block = \
"""
    <div class="alert alert-light mb-4 bg-white" style="border-style: none">
        <h4 class="text-center">iLEAPP contributors</h4>
        <ul class="list-group" style="max-width: 500px; margin:auto">
            {}
        </ul>
    </div>
"""
blog_icon = '<i class="fab fa-blogger-b fa-fw"></i>'
twitter_icon = '<i class="fab fa-twitter fa-fw"></i>'
github_icon = '<i class="fab fa-github fa-fw"></i>'
blank_icon = '<i class="fab fa-fw"></i>'
individual_contributor = \
"""
            <li class="list-group-item d-flex justify-content-between align-items-center bg-white"><i class="fas fa-medal"></i>{}
                <span>
                    {}
                </span>
            </li>
"""
""" sample contibutor data..
                    <a href="{}" target="_blank"><i class="fab fa-blogger-b fa-fw"></i></a> &nbsp;
                    <a href="{}" target="_blank"><i class="fab fa-twitter fa-fw"></i></a> &nbsp;
                    <a href="{}" target="_blank"><i class="fab fa-github fa-fw"></i></a>
"""
body_main_trailer = \
"""
            </main>
        </div>
    </div>
"""

body_end = \
"""
    <!-- End your project here-->

    <!-- jQuery -->
    <script type="text/javascript" src="_elements/MDB-Free_4.13.0/js/jquery.min.js"></script>
    <!-- Bootstrap tooltips -->
    <script type="text/javascript" src="_elements/MDB-Free_4.13.0/js/popper.min.js"></script>
    <!-- Bootstrap core JavaScript -->
    <script type="text/javascript" src="_elements/MDB-Free_4.13.0/js/bootstrap.js"></script>
    <!-- MDB core JavaScript -->
    <script type="text/javascript" src="_elements/MDB-Free_4.13.0/js/mdb.min.js"></script>
    <!-- Your custom scripts -->
    <!-- MDBootstrap Datatables  -->
    <script type="text/javascript" src="_elements/MDB-Free_4.13.0/js/addons/datatables.min.js"></script>
    <script>
        feather.replace()
    </script>
"""
nav_bar_script = \
"""
    <script>
        feather.replace();
        var element = document.getElementById("sidebar_id");
        var searchParams = new URLSearchParams(window.location.search);
        if (searchParams.has('navpos')) {
            var nav_pos = parseInt(searchParams.get('navpos'));
            if (!isNaN(nav_pos))
                element.scrollTop = nav_pos;
        }
    </script>
"""

nav_bar_script_footer = \
"""
    <script>
        var elemScrollTop = document.getElementById("sidebar_id").scrollTop.toString();
        document.addEventListener("DOMContentLoaded", function() {
            var element = document.getElementById("sidebar_id");
            element.addEventListener("scroll", function() {
                elemScrollTop = document.getElementById("sidebar_id").scrollTop.toString();
            });
        });
        $('a.nav-link').click(function(e) {
            e.preventDefault();
            location.href = $(this).attr('href') + "?navpos=" + elemScrollTop;
        });
    </script>
"""
default_responsive_table_script = \
"""
    <script>
        $(document).ready(function() {
            $('.table').DataTable({
                //"scrollY": "60vh",
                //"scrollX": "10%",
                //"scrollCollapse": true,
                "aLengthMenu": [[ 15, 50, 100, -1 ], [ 15, 50, 100, "All" ]],
            });
            $('.dataTables_length').addClass('bs-select');
            $('#mySpinner').remove();
            //$('#infiniteLoading').remove();
        });
    </script>
"""

page_footer = \
"""
    </body>
</html>
"""
