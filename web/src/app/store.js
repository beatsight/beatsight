import { configureStore } from '@reduxjs/toolkit'
import headerSlice from '../features/common/headerSlice'
import modalSlice from '../features/common/modalSlice'
// import rightDrawerSlice from '../features/common/rightDrawerSlice'
import projectsSlice from '../features/projects/projectSlice'

const combinedReducer = {
  header : headerSlice,
  // rightDrawer : rightDrawerSlice,
  modal : modalSlice,
  project : projectsSlice
}

export default configureStore({
    reducer: combinedReducer
})
