from qiniu import Auth, put_file, etag, put_data
import qiniu.config
# 需要填写你的 Access Key 和 Secret Key
access_key = 'Nj_a1F7Nqf8lrXx8r6f3QUioOdt48o7r-RzXuqT8'
secret_key = 'nUi7wLxkm_y1NEt-O22PFJHIFZWd8kJyde7e41lV'


def storage(file_data):
    """
    上传文件到七牛
    :return:
    """
    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    # 要上传的空间
    bucket_name = 'ihome-yms'
    # 上传后保存的文件名

    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)

    ret, info = put_data(token, None, file_data)

    if info.status_code == 200:
        # 上传成功
        return ret.get('key')
    else:
        return Exception('上传七牛失败')
