import {
    Alert,
    Button,
    Card,
    Col,
    Form,
    Input,
    message,
    Row,
    Space,
    Tag,
} from 'antd'
import { threatconf } from '@/service'
import { inject, observer } from 'mobx-react'
import React, { useEffect, useState } from 'react'

function ThreatinfoConfig() {
    const [form] = Form.useForm()
    const [loading, setLoading] = useState(false)
    const [saving, setSaving] = useState(false)
    const [testStatus, setTestStatus] = useState('')
    const statusText = { ok: '连接正常', fail: '连接失败' }
    const statusColor = { ok: 'green', fail: 'red' }

    useEffect(() => {
        threatconf('get').then(res => {
            const data = res && res[0] ? res[0] : {}
            form.setFieldsValue(data)
        })
    }, [form])

    const handleSave = () => {
        form.validateFields()
            .then(values => {
                setSaving(true)
                return threatconf('save', values)
            })
            .then(res => {
                setSaving(false)
                const d = res && res[0] ? res[0] : {}
                if (d.code === 200) {
                    message.success(d.msg || '保存成功')
                } else {
                    message.error(d.msg || '保存失败')
                }
            })
            .catch(() => setSaving(false))
    }

    const handleTest = () => {
        setLoading(true)
        threatconf('test')
            .then(res => {
                setLoading(false)
                const d = res && res[0] ? res[0] : {}
                if (d.code === 200) {
                    message.success(d.msg || '连接正常')
                    setTestStatus('ok')
                } else {
                    message.warning(d.msg || '连接失败')
                    setTestStatus('fail')
                }
            })
            .catch(() => {
                setLoading(false)
                setTestStatus('fail')
            })
    }

    return (
        <div>
            <Alert
                type='info'
                showIcon
                message='威胁情报服务配置'
                description='威胁情报为远程商业服务。配置后，系统检测到可疑 IP / 域名时会调用远程威胁情报服务进行关联查询（threatinfo 单点查询 / threatinfopro 批量查询）。未配置时接口返回 key invalid，前端自动降级展示，不影响其他功能。'
                style={{ marginBottom: 16 }}
            />
            <Row gutter={[16, 16]}>
                <Col span={12}>
                    <Card
                        title={
                            <Space>
                                单点威胁情报查询
                                <Tag color='geekblue'>threatinfo</Tag>
                            </Space>
                        }
                        size='small'
                    >
                        <Form form={form} layout='vertical'>
                            <Form.Item
                                name='key'
                                label='服务 KEY'
                                extra='threatinfo 鉴权密钥（保存至 tisrs.conf）'
                            >
                                <Input.Password
                                    placeholder='请输入服务 KEY'
                                    autoComplete='new-password'
                                />
                            </Form.Item>
                            <Form.Item name='tisrs_host' label='服务地址 HOST'>
                                <Input placeholder='如 127.0.0.1 或 ti.example.com' />
                            </Form.Item>
                            <Form.Item name='tisrs_port' label='服务端口 PORT'>
                                <Input placeholder='如 8091' />
                            </Form.Item>
                        </Form>
                    </Card>
                </Col>
                <Col span={12}>
                    <Card
                        title={
                            <Space>
                                批量威胁情报查询
                                <Tag color='geekblue'>threatinfopro</Tag>
                            </Space>
                        }
                        size='small'
                    >
                        <Form form={form} layout='vertical'>
                            <Form.Item
                                name='api_key'
                                label='服务 API_KEY'
                                extra='threatinfopro 鉴权密钥（保存至 tic.conf）'
                            >
                                <Input.Password
                                    placeholder='请输入服务 API_KEY'
                                    autoComplete='new-password'
                                />
                            </Form.Item>
                            <Form.Item name='tic_host' label='服务地址 HOST'>
                                <Input placeholder='如 127.0.0.1 或 ti.example.com' />
                            </Form.Item>
                            <Form.Item name='tic_port' label='服务端口 PORT'>
                                <Input placeholder='如 8091' />
                            </Form.Item>
                        </Form>
                    </Card>
                </Col>
            </Row>
            <Space style={{ marginTop: 16 }}>
                <Button type='primary' loading={saving} onClick={handleSave}>
                    保存配置
                </Button>
                <Button loading={loading} onClick={handleTest}>
                    测试连接
                </Button>
                {testStatus ? (
                    <Tag color={statusColor[testStatus]}>
                        {statusText[testStatus]}
                    </Tag>
                ) : null}
            </Space>
        </div>
    )
}

export default inject('configStore')(observer(ThreatinfoConfig))
