# vkPublicInfoExtractor
Simple python 2.7 implementation of public info extractor from vk.com by user_id

# Dependencies
`pip install vk`

`pip install gzip`

`pip install json`

`pip install json_lines`

# Usage
`extractor = vkExtractor() # creating instance of extractor`

`data = extractor.extract_info(some_user_id) # info extracting`

`extractor.write_jl_gz('some_file_path.jl.gz', data) # saving data to compressed file`

`extractor.write_jl('some_file_path.jl', data) # or saving data to file as it is`
