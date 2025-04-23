def should_include_instance(instance, tags, match_all_tags):
    instance_tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
    if match_all_tags:
        return all(k in instance_tags and instance_tags[k] == v for k, v in tags.items())
    return any(k in instance_tags and instance_tags[k] == v for k, v in tags.items())
