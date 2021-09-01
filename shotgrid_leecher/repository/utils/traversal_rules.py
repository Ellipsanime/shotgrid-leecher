ENTITY_TRAVERSAL_RULES = {
    "entity_structure": {
        "TaskTemplate": {"parent_key": [], "corresponding_key": ["id"]},
        "Asset": {"parent_key": [], "corresponding_key": ["code"]},
        "Episode": {"parent_key": [], "corresponding_key": ["code"]},
        "Sequence": {"parent_key": ["episode"], "corresponding_key": ["code"]},
        "Shot": {
            "parent_key": ["sg_sequence", "sg_episode", "sg_link"],
            "corresponding_key": ["code"],
        },
        "Task": {
            "parent_key": ["entity"],
            "corresponding_key": ["content", "entity"],
        },
        "Version": {
            "parent_key": ["sg_task", "entity"],
            "corresponding_key": ["code", "entity"],
        },
        "PublishedFile": {
            "parent_key": [
                "published_file_sg_file_dependencies_published_files",
                "sg_versions",
                "version_sg_snapshot_files_versions",
                "sg_versions_1",
                "entity",
            ],
            "corresponding_key": ["path_cache"],
        },
    },
    "fields_blacklist": [
        "filmstrip_image",
        "image",
        "step_0",
        "otio_playable",
        "sg_checksum",
        "image_source_entity",
        "viewed_by_current_user_at",
        "path_cache_storage",
    ],
}
