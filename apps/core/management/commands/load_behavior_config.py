"""
从 testcase-kit 加载生成行为配置到 TestHub 配置中心
Usage: python manage.py load_behavior_config
"""
import json
import os
from django.core.management.base import BaseCommand
from apps.core.models import GenerationBehaviorConfig


class Command(BaseCommand):
    help = '从 testcase-kit fixture 加载测试用例生成行为配置到数据库'

    def handle(self, *args, **options):
        fixture_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'fixtures', 'testcase_kit_behavior_config.json'
        )
        fixture_path = os.path.abspath(fixture_path)

        if not os.path.exists(fixture_path):
            self.stdout.write(self.style.ERROR(f'Fixture not found: {fixture_path}'))
            return

        with open(fixture_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        meta = data['_meta']
        self.stdout.write(self.style.SUCCESS(f"Loading config from {meta['source_project']} v{meta['source_version']}"))

        # 定义配置项映射
        config_items = [
            {
                'config_type': 'test_conventions',
                'config_key': 'test_conventions_v1.2',
                'name': '测试用例生成格式规范',
                'data': data.get('test_conventions', {}),
                'description': 'XMind层级结构、命名风格、优先级定义、Excel列定义、测试数据规则、步骤书写规则',
            },
            {
                'config_type': 'risk_catalog',
                'config_key': 'risk_catalog_v1.0',
                'name': '风险检查规则目录',
                'data': data.get('risk_catalog', {}),
                'description': '14条高风险漏测提醒规则，用于生成后自检（权限/列表/树形/批量/跨端/通知/重复/状态/表单/导入导出/日志/缓存/角色/附件）',
            },
            {
                'config_type': 'test_patterns',
                'config_key': 'test_pattern_catalog_v1.0',
                'name': '测试模式库',
                'data': data.get('test_pattern_catalog', {}),
                'description': '10个功能类型→标准测试矩阵（角标/导航/列表/推送/跨端/筛选/空状态/树形/批量/弹窗）',
            },
            {
                'config_type': 'generation_rules',
                'config_key': 'generation_behavior_v1.0',
                'name': 'AI生成行为规则',
                'data': data.get('generation_behavior_config', {}),
                'description': '核心原则（保真优先/原始输入第一/Scope Gate/防压缩）+ 三段式自检（Coverage/Fidelity/Grouping）+ 页面类型判断',
            },
            {
                'config_type': 'workflow',
                'config_key': 'workflow_reference_v1.0',
                'name': '生成工作流参考配置',
                'data': data.get('workflow_reference', {}),
                'description': 'Stage0输入处理→Stage1读知识层→Stage2生成→Stage3自检→Stage4导出全链路配置',
            },
        ]

        created_count = 0
        updated_count = 0

        for item in config_items:
            obj, created = GenerationBehaviorConfig.objects.update_or_create(
                config_key=item['config_key'],
                defaults={
                    'name': item['name'],
                    'config_type': item['config_type'],
                    'config_data': item['data'],
                    'source_project': meta['source_project'],
                    'source_version': meta['source_version'],
                    'description': item['description'],
                    'is_active': True,
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✅ Created: {item["name"]}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'  🔄 Updated: {item["name"]}'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Done! {created_count} created, {updated_count} updated. '
            f'Total {len(config_items)} behavior configs loaded.'
        ))
