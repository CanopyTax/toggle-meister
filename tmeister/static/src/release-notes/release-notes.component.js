import React, { useState } from 'react'
import { Container, Paper, Typography, Button } from '@material-ui/core'
import { makeStyles } from '@material-ui/core/styles'
import ErrorBoundary from '../common/error-boundary.component.js'
import ReleaseNoteTable from './release-notes-table/release-notes-table.component.js'
import { useFetchReleaseNotes } from './release-notes.hooks.js'
import CreateEditReleaseNote from './create-edit/create-edit.component.js'

const useStyles = makeStyles(theme => ({
  header: {
    marginBottom: '8px',
    display: 'flex',
    justifyContent: 'space-between',
  },
  controls: {
    marginBottom: '16px'
  },
  container: {
    padding: 16,
  }
}))

export default function Releases(props) {
  const classes = useStyles()
  const [ loading, releaseNotes, refetchReleaseNotes ] = useFetchReleaseNotes()
  const [ createNote, setCreateNote ] = useState(false)
  return (
    <ErrorBoundary>
      <Container>
        <Paper className={classes.container}>
          <div className={classes.header}>
            <Typography variant='h2'>
              Release notes
            </Typography>
            <div className={classes.controls}>
              <Button
                variant='contained'
                color='primary'
                onClick={() => setCreateNote(true)}
              >
                Create Release note
              </Button>
            </div>
          </div>
          <ReleaseNoteTable
            loading={loading}
            releaseNotes={releaseNotes}
            refetch={refetchReleaseNotes}
          />
          {
            createNote && (
              <CreateEditReleaseNote
                close={() => setCreateNote(false)}
                onSuccess={refetchReleaseNotes}
              />
            )
          }
        </Paper>
      </Container>
    </ErrorBoundary>
  )
}

