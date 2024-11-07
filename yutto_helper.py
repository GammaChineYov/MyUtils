# B站视频下载工具
import functools
import subprocess
import typing
import enum


# 视频清晰度枚举类
class VideoQualityEnum(enum.Enum):
    _8K_ULTRA_HD = "127"
    DOLBY_VISION = "126"
    HDR_TRUE_COLOR = "125"
    _4K_SUPER_CLEAR = "120"
    _1080P_60FPS = "116"
    _1080P_HIGH_BITRATE = "112"
    INTELLIGENT_REPAIR = "100"
    _1080P_HD = "80"
    _720P_60FPS = "74"
    _720P_HD = "64"
    _480P_CLEAR = "32"
    _360P_SMOOTH = "16"


# 音频码率枚举类
class AudioQualityEnum(enum.Enum):
    HI_RES = "30251"
    DOLBY_AUDIO = "30255"
    DOLBY_ATMOS = "30250"
    _320KBPS = "30280"
    _128KBPS = "30232"
    _64KBPS = "30216"


# 视频编码枚举类
class VideoCodecEnum(enum.Enum):
    AV1 = "av1"
    HEVC = "hevc"
    AVC = "avc"


# 音频编码枚举类
class AudioCodecEnum(enum.Enum):
    MP4A = "mp4a"


# 输出格式枚举类（视频流存在时）
class OutputFormatEnum(enum.Enum):
    INFER = "infer"
    MP4 = "mp4"
    MKV = "mkv"
    MOV = "mov"


# 输出格式枚举类（仅音频流时）
class OutputFormatAudioOnlyEnum(enum.Enum):
    INFER = "infer"
    AAC = "aac"
    MP3 = "mp3"
    FLAC = "flac"
    MP4 = "mp4"
    MKV = "mkv"
    MOV = "mov"


# 弹幕格式枚举类
class DanmakuFormatEnum(enum.Enum):
    ASS = "ass"
    XML = "xml"
    PROTOBUF = "protobuf"


# 代理设置枚举类
class ProxyEnum(enum.Enum):
    AUTO = "auto"
    NO = "no"
    CUSTOM = "custom"  # 用于表示自定义的代理服务器地址


# 资源选择枚举类（用于表示仅下载视频流或音频流等布尔类型的扩展）
class ResourceSelectionEnum(enum.Enum):
    YES = "yes"
    NO = "no"


# 音频格式枚举类
class AudioFormatEnum(enum.Enum):
    MP3 = "mp3"
    AAC = "aac"
    FLAC = "flac"




def set_param_dec(param_flag, is_no_value=False, expected_type=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, value=None):
            nonlocal expected_type, is_no_value
            param_name = func.__name__.split('set_')[1]
            if not is_no_value and expected_type is None:
                expected_type = typing.get_type_hints(getattr(self, func.__name__))[param_name]
            self._set_param(param_name, param_flag, value, is_no_value, expected_type)
            return self
        return wrapper
    return decorator


class HelperBase:
    def __init__(self, command_name):
        # 存储所有参数的字典
        self.params_dict = {}
        self.command_name = command_name

    def _validate_enum_parameter(self, value, expected_type):
        if expected_type and not isinstance(value, expected_type):
            raise TypeError(f"Parameter must be an appropriate {expected_type.__name__} instance")

    def _set_param(self, param_name, param_flag, value, is_no_value=False, expected_type=None):
        if is_no_value:
            self.params_dict[param_flag] = None
        else:
            self._validate_enum_parameter(value, expected_type)
            # 如果是enum类型的话取值
            if isinstance(value, enum.Enum):
                self.params_dict[param_flag] = value.value
            else:
                self.params_dict[param_flag] = value

    def Excecute(self):
        command = [self.command_name]
        for key, value in self.params_dict.items():
            if value is None:
                command.append(key)
            else:
                command.extend([key, str(value)])
                # command.append(f"{key}={value}")
        print(command)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        print(stdout.decode('utf-8'))
        print(stderr.decode('utf-8'))


class YuttoHelper(HelperBase):
    def __init__(self, url: str):
        super().__init__("yutto")
        self.url = url
        self.params_dict[url] = None
        # 新增对其他 Enum 类的简写访问属性
        self.VQ = VideoQualityEnum
        self.AQ = AudioQualityEnum
        self.VC = VideoCodecEnum
        self.AC = AudioCodecEnum
        self.OF = OutputFormatEnum
        self.OFAO = OutputFormatAudioOnlyEnum
        self.DF = DanmakuFormatEnum
        self.PX = ProxyEnum
        self.RS = ResourceSelectionEnum
        self.AF = AudioFormatEnum

    @set_param_dec("-d")
    def set_video_dir(self, video_dir: str):
        """设置视频存储目录。"""
        return self

    @set_param_dec("-d")
    def set_audio_dir(self, audio_dir: str):
        """设置音频存储目录。"""
        return self

    @set_param_dec("-q")
    def set_video_quality(self, video_quality: VideoQualityEnum):
        """设置视频清晰度。"""
        return self

    @set_param_dec("--vcodec")
    def set_video_codec(self, video_codec: VideoCodecEnum):
        """设置视频编码。"""
        return self

    @set_param_dec("-aq")
    def set_audio_quality(self, audio_quality: AudioQualityEnum):
        """设置音频码率。"""
        return self

    @set_param_dec("--audio-only", is_no_value=True)
    def set_audio_only(self):
        """设置是否仅下载音频。"""
        return self

    @set_param_dec("-df")
    def set_danmaku_format(self, danmaku_format: DanmakuFormatEnum):
        """设置弹幕格式。"""
        return self

    @set_param_dec("-d")
    def set_root_dir(self, root_dir: "str"):
        """设置存放根目录。"""
        return self

    @set_param_dec("--tmp-dir")
    def set_tmp_dir(self, tmp_dir: str):
        """设置临时文件目录。"""
        return self

    @set_param_dec("-c")
    def set_cookies(self, cookies: str):
        """设置 Cookies。"""
        return self

    @set_param_dec("-n")
    def set_num_workers(self, num_workers: int):
        """设置并行 worker 数量。"""
        return self

    @set_param_dec("--download-vcodec-priority")
    def set_download_vcodec_priority(self, download_vcodec_priority: str):
        """设置视频下载编码优先级。"""
        return self

    @set_param_dec("--output-format")
    def set_output_format(self, output_format: OutputFormatEnum):
        """设置至少包含视频流时的输出格式。"""
        return self

    @set_param_dec("--output-format-audio-only")
    def set_output_format_audio_only(self, output_format_audio_only: OutputFormatAudioOnlyEnum):
        """设置仅包含音频流时的输出格式。"""
        return self

    @set_param_dec("--vip-strict", is_no_value=True)
    def set_vip_strict(self):
        """设置是否严格校验大会员状态。"""
        return self

    @set_param_dec("--login-strict", is_no_value=True)
    def set_login_strict(self):
        """设置是否严格校验登录状态。"""
        return self

    @set_param_dec("--download-interval")
    def set_download_interval(self, download_interval: int):
        """设置两话之间的下载间隔（单位为秒）。"""
        return self

    @set_param_dec("--banned-mirrors-pattern")
    def set_banned_mirrors_pattern(self, banned_mirrors_pattern: str):
        """设置禁用下载镜像的正则表达式。"""
        return self

    @set_param_dec("--no-color", is_no_value=True)
    def set_no_color(self):
        """设置是否不显示颜色。"""
        return self

    @set_param_dec("--no-progress", is_no_value=True)
    def set_no_progress(self):
        """设置是否不显示进度条。"""
        return self

    @set_param_dec("--debug", is_no_value=True)
    def set_debug(self):
        """设置是否启用 Debug 模式。"""
        return self

    @set_param_dec("--no-danmaku", is_no_value=True)
    def set_no_danmaku(self):
        """设置不生成弹幕文件。"""
        return self

    @set_param_dec("--danmaku-only", is_no_value=True)
    def set_danmaku_only(self):
        """设置仅生成弹幕文件。"""
        return self

    @set_param_dec("--no-subtitle", is_no_value=True)
    def set_no_subtitle(self):
        """设置不生成字幕文件。"""
        return self

    @set_param_dec("--batch", is_no_value=True)
    def set_batch(self):
        """设置是否批量下载。"""
        return self

    @set_param_dec("-p")
    def set_episodes_value(self, episodes_value: str):
        """设置批量下载选集值。"""
        return self

    @set_param_dec("--with-section", is_no_value=True)
    def set_with_section(self):
        """设置是否同时下载附加剧集。"""
        return self

    @set_param_dec("--batch-filter-start-time")
    def set_batch_filter_start_time(self, batch_filter_start_time: str):
        """设置批量下载开始时间。"""
        return self

    @set_param_dec("--batch-filter-end-time")
    def set_batch_filter_end_time(self, batch_filter_end_time: str):
        """设置批量下载结束时间。"""
        return self

    @set_param_dec("-bs")
    def set_block_size(self, block_size: float):
        """设置下载块大小。"""
        return self

    @set_param_dec("-w", is_no_value=True)
    def set_overwrite(self):
        """设置是否强制覆盖已下载文件。"""
        return self

    @set_param_dec("-tp")
    def set_subpath_template(self, subpath_template: str):
        """设置存放子路径模板。"""
        return self

    @set_param_dec("-af")
    def set_alias_file(self, alias_file: str):
        """设置 url 别名文件路径。"""
        return self

    @set_param_dec("--metadata-format-premiered")
    def set_metadata_format_premiered(self, metadata_format_premiered: str):
        """设置指定媒体元数据值的格式。"""
        return self
    
    def Download(self):
        self.Excecute()


# |参数标志|默认值|参数范围|作用|
# |--|--|--|--|
# |`-n`或`--num-workers`|`8`|正整数|限制最大并行Worker数量|
# |`-q`或`--video-quality`|`127`|`127` \| `126` \| `125` \| `120` \| `116` \| `112` \| `100` \| `80` \| `74` \| `64` \| `32` \| `16`|指定视频清晰度等级|
# |`-aq`或`--audio-quality`|`30251`|`30251` \| `30255` \| `30250` \| `30280` \| `30232` \| `30216`|指定音频码率等级|
# |`--vcodec`|`"avc:copy"`|下载编码：`"av1"` \| `"hevc"` \| `"avc"`；保存编码：FFmpeg所有可用的视频编码器|指定视频编码|
# |`--acodec`|`"mp4a:copy"`|下载编码：`"mp4a"`；保存编码：FFmpeg所有可用的音频编码器|指定音频编码|
# |`--download-vcodec-priority`|`"auto"`|`"auto"`或者使用`,`分隔的下载编码列表，如`"hevc,avc,av1"`|指定视频下载编码优先级|
# |`--output-format`|`"infer"`|`"infer"` \| `"mp4"` \| `"mkv"` \| `"mov"`|指定至少包含视频流时的输出格式|
# |`--output-format-audio-only`|`"infer"`|`"infer"` \| `"aac"` \| `"mp3"` \| `"flac"` \| `"mp4"` \| `"mkv"` \| `"mov"`|指定仅包含音频流时的输出格式|
# |`-df`或`--danmaku-format`|`"ass"`|`"ass"` \| `"xml"` \| `"protobuf"`|指定弹幕格式|
# |`-bs`或`--block-size`|`0.5`|正实数（以MiB为单位）|设置下载块大小|
# |`-w`或`--overwrite`|`False`|布尔值|强制覆盖已下载文件|
# |`-x`或`--proxy`|`"auto"`|`"auto"` \| `"no"` \| `<https?://url/to/proxy/server>`|设置代理服务器|
# |`-d`或`--dir`|`"./"`|字符串（路径）|设置存放根目录|
# |`--tmp-dir`|`存放根目录的值`|字符串（路径）|设置临时文件目录|
# |`-c`或`--sessdata`|`""`|字符串|设置Cookies|
# |`-tp`或`--subpath-template`|`"{auto}"`|包含`title` \| `id` \| `name` \| `username` \| `series_title` \| `pubdate` \| `download_date` \| `owner_uid`等变量的字符串（符合Python format函数模板语法）|设置存放子路径模板|
# |`-af`或`--alias-file`|`None`|字符串（路径）或`-`（从标准输入读取）|指定别名文件路径|
# |`--metadata-format-premiered`|`"%Y-%m-%d"`|`"%Y-%m-%d"` \| `"%Y-%m-%d %H:%M:%S"`|指定媒体元数据值的格式（当前仅支持`premiered`）|
# |`--vip-strict`|`False`|布尔值|严格校验大会员状态|
# |`--login-strict`|`False`|布尔值|严格校验登录状态|
# |`--download-interval`|`0`|非负整数（单位为秒）|设置两话之间的下载间隔|
# |`--banned-mirrors-pattern`|`None`|正则表达式字符串|禁用下载镜像|
# |`--no-color`|`False`|布尔值|不显示颜色|
# |`--no-progress`|`False`|布尔值|不显示进度条|
# |`--debug`|`False`|布尔值|启用Debug模式|
# |`--video-only`|`False`|布尔值|仅下载视频流|
# |`--audio-only`|`False`|布尔值|仅下载音频流|
# |`--no-danmaku`|`False`|布尔值|不生成弹幕文件|
# |`--danmaku-only`|`False`|布尔值|仅生成弹幕文件|
# |`--no-subtitle`|`False`|布尔值|不生成字幕文件|
# |`--subtitle-only`|`False`|布尔值|仅生成字幕文件|
# |`--with-metadata`|`False`|布尔值|生成媒体元数据文件|
# |`--metadata-only`|`False`|布尔值|仅生成媒体元数据文件|
# |`--no-cover`|`False`|布尔值|不生成视频封面|
# |`--no-chapter-info`|`False`|布尔值|不生成章节信息|
# |`--danmaku-font-size`|`video_width / 40`|正实数（与视频宽度相关）|设置弹幕字体大小|
# |`--danmaku-font`|`"SimHei"`|字符串|设置弹幕字体|
# |`--danmaku-opacity`|`0.8`|`0`到`1`之间的实数|设置弹幕不透明度|
# |`--danmaku-display-region-ratio`|`1.0`|正实数|设置弹幕显示区域与视频高度的比例|
# |`--danmaku-speed`|`1.0`|正实数|设置弹幕速度|
# |`--danmaku-block-top`|`False`|布尔值|屏蔽顶部弹幕|
# |`--danmaku-block-bottom`|`False`|布尔值|屏蔽底部弹幕|
# |`--danmaku-block-scroll`|`False`|布尔值|屏蔽滚动弹幕|
# |`--danmaku-block-reverse`|`True`|布尔值|屏蔽逆向弹幕|
# |`--danmaku-block-fixed`|`False`|布尔值|屏蔽固定弹幕（顶部、底部）|
# |`--danmaku-block-special`|`False`|布尔值|屏蔽高级弹幕|
# |`--danm Aku-block-colorful`|`False`|布尔值|屏蔽彩色弹幕|
# |`--danmaku-block-keyword-patterns`|`None`|正则表达式字符串（用`,`分隔）|屏蔽关键词|
# |`-b`或`--batch`|`False`|布尔值|启用批量下载|
# |`-p`或`--episodes`|`1~-1`|`<p1>`（单独下某一剧集，支持负数来选择倒数第几话，还可以使用`$`来代表`-1`） \| `<p_start>~<p_end>`（使用`~`可以连续选取，如果起始为1，或者终止为-1则可以省略） \| `<p1>,<p2>,<p3>,...,<pn>`（使用`,`可以不连续选取）|设置批量下载选集|
# |`-s`或`--with-section`|`False`|布尔值|同时下载附加剧集|
# |`--batch-filter-start-time`和`--batch-filter-end-time`|`不限制`|`%Y-%m-%d` \| `%Y-%m-%d %H:%M:%S`|指定稿件发布时间范围进行批量下载（左闭右开区间）|

    # "视频文件",
    # "音频文件",
    # "弹幕文件（可设置是否生成或仅生成）",
    # "字幕文件（可设置是否生成）",
    # "视频清晰度等级",
    # "视频编码",
    # "音频码率等级",
    # "指定视频存储目录",
    # "指定音频存储目录",
    # "指定输出格式（视频流存在时）",
    # "指定输出格式（仅音频流时）",
    # "指定弹幕格式",
    # "批量下载选集",
    # "批量下载附加剧集",
    # "指定稿件发布时间范围进行批量下载"