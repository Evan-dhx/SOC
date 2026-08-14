import { deviceApi } from '@/service'
import { Form } from 'antd'
import { inject, observer } from 'mobx-react'
import React, { useEffect, useMemo } from 'react'
import {
    DefaultFormItem,
    DefaultFormItemSelect,
    DisabledSelect,
    IpInput,
    PortInput,
    PskInput,
    ProxySelect,
} from '../../form/form-components'
import AddConfigModal, { AddConfigModalStore } from '../modal-config'
import { commonFormProps, getConfirmInfo, getFormDict } from '../utils'

const deviceModalStore = new AddConfigModalStore()

const formArr = [
    <DefaultFormItem
        name='name'
        key='name'
        label='名称'
        rules={[
            {
                required: true,
                message: '请输入名称！',
            },
        ]}
    />,
    <IpInput name='ip' key='ip' label='采集节点IP' />,
    <ProxySelect name='agentid' key='agentid' label='分析节点' />,
    <PortInput
        name='port'
        key='port'
        label='分析节点端口'
        rules={[
            {
                required: true,
                message: '请输入分析节点端口！',
            },
        ]}
    />,
    <DefaultFormItemSelect
        name='pcap_level'
        key='pcap_level'
        label='数据包留存级别'
        inputProps={{
            defaultValue: 1,
            options: [
                {
                    key: 0,
                    value: 0,
                    label: '不留存',
                },
                {
                    key: 1,
                    value: 1,
                    label: '只留存威胁',
                },
                {
                    key: 2,
                    value: 2,
                    label: '威胁和资产',
                },
                {
                    key: 3,
                    value: 3,
                    label: '所有会话一对',
                },
            ],
        }}
    />,
    <DefaultFormItem name='interface' key='interface' label='采集网卡名称' />,
    <DefaultFormItem name='filter' key='filter' label='流量采集过滤' />,
    <DefaultFormItem name='template' key='template' label='流量元数据模板' />,
    <PskInput
        name='psk'
        key='psk'
        label='传输密钥PSK'
        placeholder='留空=明文直连；填写后探针→接收端使用 TLS 加密传输'
    />,
    <DisabledSelect name='disabled' key='disabled' label='禁止使用' />,
    <DefaultFormItem name='comment' key='comment' label='注释' />,
]

const dict = getFormDict(formArr)

function DeviceForm({ form, setDisabledNext }) {
    useEffect(() => {
        if (setDisabledNext) setDisabledNext(false)
    }, [setDisabledNext])
    return (
        <Form
            form={form}
            className='form-in-modal'
            name='DeviceModalForm'
            initialValues={{
                name: '',
                creator: '',
                comment: '',
                ip: '',
                port: '',
                disabled: 'N',
            }}
            {...commonFormProps}
        >
            {formArr}
        </Form>
    )
}

const forms = [
    {
        title: '采集结点',
        content: DeviceForm,
    },
]

export default inject('configStore')(
    observer(function AddDeviceModal({ configStore }) {
        const { op, visible, onClose, init, confirm, data } = deviceModalStore
        const { changeData } = configStore
        useEffect(() => {
            init(deviceApi, res => {
                changeData({ device: res })
            })
        }, [changeData, init])

        // 映射后端字段到表单字段，过滤非编辑字段
        const processedInitialValues = useMemo(() => {
            const result = { ...data }
            if (result.tls_psk) {
                result.psk = result.tls_psk
            }
            delete result.tls_psk
            delete result.tls_status
            delete result.tls_last_seen
            return result
        }, [data])

        return (
            <AddConfigModal
                op={op}
                title='采集节点'
                visible={visible}
                forms={forms}
                initialValues={processedInitialValues}
                onClose={onClose}
                onConfirm={confirm}
                getConfirmInfo={values => getConfirmInfo(values, dict)}
            />
        )
    })
)

export function openAddDeviceModal(params) {
    deviceModalStore.onOpen(params)
}
