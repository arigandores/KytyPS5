  // Track F, F42a (HPP-779, ROADMAP s122 item 694(g)(1), (v)(6)): the whole fault bitmap after the last Dispatch (its
  // submission has completed - EndSubmitAndFree waits), copied into a host-visible buffer kept for the next call (new
  // code of the stand: before F42a the harness only zeroed m_fault_buffer and destroyed it).
  std::vector<u32> ReadFaultBuffer(const char *shader_name) {
    EnsureBdaBuffers(shader_name);
    if (m_fault_readback.buffer == nullptr) {
      m_fault_readback = CreateHostBuffer(shader_name, m_fault_buffer.size,
                                          vk::BufferUsageFlagBits::eTransferDst, {});
    }
    vk::CommandBuffer cmd = BeginCommands(shader_name, "fault readback");
    vk::BufferMemoryBarrier barrier{};
    barrier.sType = vk::StructureType::eBufferMemoryBarrier;
    barrier.srcAccessMask = vk::AccessFlagBits::eShaderWrite | vk::AccessFlagBits::eTransferWrite;
    barrier.dstAccessMask = vk::AccessFlagBits::eTransferRead;
    barrier.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
    barrier.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
    barrier.buffer = m_fault_buffer.buffer;
    barrier.offset = 0;
    barrier.size = m_fault_buffer.size;
    cmd.pipelineBarrier(vk::PipelineStageFlagBits::eComputeShader | vk::PipelineStageFlagBits::eTransfer,
                        vk::PipelineStageFlagBits::eTransfer, {}, 0, nullptr, 1, &barrier, 0, nullptr);
    vk::BufferCopy region{};
    region.srcOffset = 0;
    region.dstOffset = 0;
    region.size = m_fault_buffer.size;
    cmd.copyBuffer(m_fault_buffer.buffer, m_fault_readback.buffer, 1, &region);
    barrier.srcAccessMask = vk::AccessFlagBits::eTransferWrite;
    barrier.dstAccessMask = vk::AccessFlagBits::eHostRead;
    barrier.buffer = m_fault_readback.buffer;
    barrier.size = m_fault_readback.size;
    cmd.pipelineBarrier(vk::PipelineStageFlagBits::eTransfer, vk::PipelineStageFlagBits::eHost, {}, 0, nullptr, 1,
                        &barrier, 0, nullptr);
    EndSubmitAndFree(shader_name, "fault readback", cmd);
    return ReadBuffer(shader_name, m_fault_readback, static_cast<size_t>(m_fault_buffer.size / sizeof(u32)));
  }

