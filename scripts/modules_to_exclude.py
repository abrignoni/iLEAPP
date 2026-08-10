# This list contains the filenames of artifact scripts that take a long time to run.
# These modules are deselected by default in the GUI.
#
# Entries are module filenames (the .py stem), not artifact names, so one entry covers
# every artifact a module declares.

modules_to_exclude = [
    # Apple Unified Logs. Reading the .tracev3 data in a full file system extraction is
    # the largest single job in iLEAPP: an iOS 17.1 image produced 30.4 million records in
    # 16 minutes and a 6.4 GB LAVA database, and getting there means extracting the whole
    # of uuidtext (hundreds of megabytes) before parsing starts. Worth every second when
    # Unified Logs are what the case turns on, and worth nothing at all otherwise, so the
    # examiner opts in rather than paying for it on every run.
    'c2paProvenance',
    'logarchive',
    'Ph008HasAdjustment',
    'Ph009BurstAvalanche',
    'Ph011KwrdsCapsTitlesDescripsBasicAssetData',
    'Ph015PeopleandDetFacesNAD',
    'Ph016AssetPeopleandDetFaces',
    'Ph017GenAIDetected',
    'Ph020AlbumsNAD',
    'Ph021AlbumsNonSharedNAD',
    'Ph022AssetsInNonSharedAlbums',
    'Ph023AlbumsSharedNAD',
    'Ph025SWYConvAlbumsNAD',
    'Ph024AssetsInSharedAlbums',
    'Ph026SyndicationPLAssets',
    'Ph030iCloudShareMethodsNAD',
    'Ph031iCloudSharePhotoLibraryNAD',
    'Ph032AssetsIniCldSPLwContrib',
    'Ph033AssetsIniCldSPLfromOtherContrib',
    'Ph034iCloudSharedLinksNAD',
    'Ph035iCloudSharedLinkAssets',
    'Ph050AssetIntResouData',
    'Ph051PossOptimizedAssetsIntResouData',
    'Ph094Ios14REFforAssetAnalysis',
    'Ph095iOS15REFforAssetAnalysis',
    'Ph096iOS16REFforAssetAnalysis',
    'Ph097iOS17REFforAssetAnalysis',
    'Ph098iOS18REFforAssetAnalysis',
    'Ph126iOS26REFforAssetAnalysis',
    'photosDbexif',
    'photosMetadata',
    'walStrings',
]
