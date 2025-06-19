import React from 'react';
import { FaDiceD20 } from 'react-icons/fa';
import styles from './Loading.module.css';

function Loading() {
  return (
    <div className={styles.loadingContainer}>
      <FaDiceD20 className={styles.diceIcon} />
      <div className={styles.loadingText}>
        Loading
        <span className={styles.dot}>.</span>
        <span className={styles.dot}>.</span>
        <span className={styles.dot}>.</span>
      </div>
    </div>
  );
}

export default Loading;
