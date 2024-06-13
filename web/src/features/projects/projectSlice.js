import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import axios from 'axios'

function isPendingAction(action) {
  return typeof action.type === 'string' && action.type.endsWith('/pending')
}

function isFulfilledAction(action) {
  return typeof action.type === 'string' && action.type.endsWith('/fulfilled')
}


function isRejectedAction(action) {
  return typeof action.type === 'string' && action.type.endsWith('/rejected')
}

export const getProjects = createAsyncThunk('/projects', async () => {
        const response = await axios.get('/api/projects/', {})
        return response.data;
})

export const projectsSlice = createSlice({
  name: 'projects',
  initialState: {
    isLoading: false,
    projects : []
  },
  reducers: {
    addNewProject: (state, action) => {
      let {newProjectObj} = action.payload
      state.projects = [...state.projects, newProjectObj]
    },
    deleteProject: (state, action) => {
      let {index} = action.payload
      state.projects.splice(index, 1)
    }
  },
extraReducers: (builder) => {
    builder
      .addCase(getProjects.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(getProjects.fulfilled, (state, action) => {
        state.projects = action.payload;
        state.isLoading = false;
      })
      .addCase(getProjects.rejected, (state) => {
        state.isLoading = false;
      });
  }  
})

export const { addNewProject, deleteProject } = projectsSlice.actions

export default projectsSlice.reducer
