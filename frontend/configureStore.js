import { applyMiddleware, createStore } from 'redux';
import ReduxPromise from 'redux-promise';
import thunkMiddleware from 'redux-thunk';
import rootReducer from './reducers';

export default function configureStore(preloadedState) {
  const middlewares = [thunkMiddleware, ReduxPromise];
  const middlewareEnhancer = applyMiddleware(...middlewares);

  const store = createStore(rootReducer, preloadedState, middlewareEnhancer);

  return store;
}
