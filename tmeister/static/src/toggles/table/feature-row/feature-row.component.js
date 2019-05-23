import React, { useState } from 'react'
import styles from './feature-row.styles.css'
import DeleteFeatureModal from '../../delete/delete-feature-modal.component.js'
import { useDeleteFeature, useChangeFeatureStatus } from '../../toggles.hooks.js'

export default function FeatureRow (props) {
  const { featureName, groupOfToggles, refetchToggles } = props
  const [ deleteConfirmModal, setDeleteConfirmModal ] = useState(false)
  const [ deleteFeatureByName, deleteInProgress ] = useDeleteFeature(refetchToggles)
  const [ setToggleToChange, setNewState ] = useChangeFeatureStatus(refetchToggles)
  return (
    <tr className="+hover">
      <td className={styles.featureName}>
        <div>
          {featureName}
        </div>
        <div className={`cps-btn-icon ${styles.buttonIcon}`}>
          <a className="cps-link" onClick={() => {setDeleteConfirmModal(true)}} >
            <span className="cps-icon cps-icon-close" />
          </a>
        </div>
      </td>
      {
        groupOfToggles
          .map(toggle => {
            return (
              <td key={toggle.toggle.env}>
                <label className="cps-toggle">
                  <input
                    type="checkbox"
                    checked={toggle.toggle.state === 'ON'}
                    onChange={() => {
                      if (toggle.toggle.state === 'ON') {
                        setNewState('OFF')
                      } else {
                        setNewState('ON')
                      }
                      setToggleToChange(toggle.toggle)
                    }}
                  />
                  <span />
                </label>
              </td>
            );
          })
      }
      {
        deleteConfirmModal && (
          <DeleteFeatureModal
            featureName={featureName}
            close={() => setDeleteConfirmModal(false)}
            performDelete={() => deleteFeatureByName(featureName)}
          />
        )
      }
    </tr>
  );
}
