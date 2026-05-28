"""
Core 应用模型
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class UnifiedNotificationConfig(models.Model):
    """统一通知配置模型 - 用于配置飞书、企微、钉钉机器人"""

    CONFIG_TYPE_CHOICES = [
        ('webhook_feishu', '飞书机器人'),
        ('webhook_wechat', '企业微信机器人'),
        ('webhook_dingtalk', '钉钉机器人'),
    ]

    name = models.CharField(max_length=100, verbose_name='配置名称', help_text='用于标识该通知配置的名称')
    config_type = models.CharField(max_length=20, choices=CONFIG_TYPE_CHOICES, default='webhook_feishu',
                                   verbose_name='配置类型')
    webhook_bots = models.JSONField(default=dict, blank=True, null=True, verbose_name='Webhook机器人配置',
                                    help_text='飞书、企微、钉钉机器人配置')
    is_default = models.BooleanField(default=False, verbose_name='是否默认配置')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建者')

    class Meta:
        db_table = 'unified_notification_configs'
        verbose_name = '统一通知配置'
        verbose_name_plural = '统一通知配置'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['config_type']),
            models.Index(fields=['is_default']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        return f"{self.name} - {self.get_config_type_display()}"

    def get_webhook_bots(self):
        """获取配置的所有webhook机器人"""
        bots = []
        if self.webhook_bots:
            for bot_type, bot_config in self.webhook_bots.items():
                bot_data = {
                    'type': bot_type,
                    'name': bot_config.get('name', f'{bot_type}机器人'),
                    'webhook_url': bot_config.get('webhook_url'),
                    'enabled': bot_config.get('enabled', True),
                    # 业务类型勾选框
                    'enable_ui_automation': bot_config.get('enable_ui_automation', True),
                    'enable_api_testing': bot_config.get('enable_api_testing', True)
                }
                # 钉钉机器人需要额外包含secret字段
                if bot_type == 'dingtalk' and bot_config.get('secret'):
                    bot_data['secret'] = bot_config.get('secret')
                bots.append(bot_data)
        return bots


class GenerationBehaviorConfig(models.Model):
    """AI 测试用例生成行为配置模型 - 存储 testcase-kit 等外部项目的生成规则"""

    CONFIG_TYPE_CHOICES = [
        ('test_conventions', '测试用例格式规范'),
        ('risk_catalog', '风险检查规则'),
        ('test_patterns', '测试模式库'),
        ('generation_rules', '生成行为规则'),
        ('workflow', '工作流配置'),
    ]

    name = models.CharField(max_length=200, verbose_name='配置名称')
    config_type = models.CharField(max_length=50, choices=CONFIG_TYPE_CHOICES, verbose_name='配置类型')
    config_key = models.CharField(max_length=100, unique=True, verbose_name='配置键', help_text='唯一标识，如 test_conventions_v1')
    config_data = models.JSONField(default=dict, verbose_name='配置数据', help_text='JSON 格式的配置内容')
    source_project = models.CharField(max_length=200, blank=True, verbose_name='来源项目', help_text='如 testcase-kit')
    source_version = models.CharField(max_length=50, blank=True, verbose_name='来源版本')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    description = models.TextField(blank=True, verbose_name='配置说明')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'generation_behavior_configs'
        verbose_name = '生成行为配置'
        verbose_name_plural = '生成行为配置'
        ordering = ['config_type', '-updated_at']
        indexes = [
            models.Index(fields=['config_type']),
            models.Index(fields=['config_key']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} [{self.config_type}]"
