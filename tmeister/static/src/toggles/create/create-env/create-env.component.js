import React, { useState } from 'react';
import CreateEnvModal from './create-env-modal.component.js';
import Button from '../../../common/simple-button/simple-button.component.js'

export default function CreateEnv (props) {
  const { refetchToggles } = props
  const [showCreateModal, setShowCreateModal] = useState(false)
  return (
    <div>
      <Button
        onClick={() => setShowCreateModal(true)}
      >
        Create environment
      </Button>
      {
        showCreateModal &&
          <CreateEnvModal
            hide={() => setShowCreateModal(false)}
            refetchToggles={refetchToggles}
          />
      }
    </div>
  );
}
