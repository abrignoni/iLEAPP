# iOS:
#   https://www.gkgigs.com/list-apple-ios-version-history/
#   https://betawiki.net/wiki/Category:IOS
#   https://theapplewiki.com/wiki/Models
# watchOS:
#   https://www.gkgigs.com/latest-watchos-version/
#   https://www.theiphonewiki.com/wiki/beta_Firmware
# tvOS:
#   https://gkgigs.com/latest-tvos-version/
#   https://www.theiphonewiki.com/wiki/beta_Firmware
# macOS:
#   https://www.gkgigs.com/list-of-all-macos-version-history/
#   https://betawiki.net/wiki/Category:MacOS_versions
# All:
# https://x.com/iSWUpdates
# https://theapplewiki.com/wiki/Firmware

from os.path import join

domains = {
    "AppDomain-": "private/var/mobile/Containers/Data/Application",
    "AppDomainGroup-": "private/var/mobile/Containers/Shared/AppGroup",
    "AppDomainPlugin-": "private/var/mobile/Containers/Data/PluginKitPlugin",
    "CameraRollDomain": "private/var/mobile",
    "DatabaseDomain": "private/var/db",
    "HealthDomain": "private/var/mobile",
    "HomeDomain": "private/var/mobile",
    "HomeKitDomain": "private/var/mobile",
    "InstallDomain": "private/var/installd",
    "KeyboardDomain": "private/var/mobile",
    "KeychainDomain": "private/var/protected/trustd/private",
    "ManagedPreferencesDomain": "private/var/Managed Preferences",
    "MediaDomain": "private/var/mobile",
    "MobileDeviceDomain": "private/var/MobileDevice",
    "NetworkDomain": "private/var/networkd",
    "ProtectedDomain": "private/var/protected",
    "RootDomain": "private/var/root",
    "SysContainerDomain-": "private/var/containers/Data/System",
    "SysSharedContainerDomain-": "private/var/containers/Shared/SystemGroup",
    "SystemPreferencesDomain": "private/var/preferences",
    "TonesDomain": "private/var/mobile",
    "WirelessDomain": "private/var/wireless"
}

region_code = {
    "AB": "Egypt, Jordan, Saudi Arabia, United Arab Emirates",
    "AM": "United States (Assembled in Vietnam)",
    "B": "Ireland, UK",
    "BR": "Brazil (Assembled in Brazil)",
    "BZ": "Brazil (Assembled in China)",
    "C": "Canada",
    "CL": "Canada",
    "CH": "China",
    "CZ": "Czech Republic",
    "D": "Germany",
    "DN": "Austria, Germany, Netherlands",
    "E": "Mexico",
    "EE": "Estonia",
    "FB": "France, Luxembourg",
    "FD": "Austria, Liechtenstein, Switzerland",
    "GR": "Greece",
    "HN": "India",
    "IP": "Italy",
    "HB": "Israel",
    "J": "Japan",
    "KH": "Korea",
    "KN": "Norway",
    "KS": "Finland, Sweden",
    "LA": "Colombia, Ecuador, El Salvador, Guatemala, Honduras, Peru",
    "LE": "Argentina",
    "LL": "USA, Canada",
    "LZ": "Chile, Paraguay, Uruguay",
    "MG": "Hungary",
    "MO": "Macau, Hong Kong",
    "MY": "Malaysia",
    "NF": "Belgium, France, Luxembourg",
    "PL": "Poland",
    "PO": "Portugal",
    "PP": "Philippines",
    "RO": "Romania",
    "RS": "Russia",
    "SL": "Slovakia",
    "SO": "South Africa",
    "T": "Italy",
    "TA": "Taiwan",
    "TU": "Turkey",
    "TY": "Italy",
    "VC": "Canada",
    "X": "Australia, New Zealand",
    "Y": "Spain",
    "ZA": "Singapore",
    "ZP": "Hong Kong, Macau",
}

platforms = {
    1: "iPad",
    2: "iPhone",
    3: "macOS",
    4: "macOS",
    6: "watchOS"
}


def get_root_path_from_domain(domain):
    if domain in domains:
        return domains[domain]
    elif '-' in domain:
        dash_position = domain.find("-") + 1
        path = domains[domain[:dash_position]]
        bundle_identifier = domain[dash_position:]
        return join(path, bundle_identifier)
    return ''
