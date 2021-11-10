import pygsheets
import pandas as pd

#authorization
gc = pygsheets.authorize(service_file='./cs321-proj3-27cd9b62ae97.json')

sample_list = [{'content': 'hw', 'priority': 'High', 'tags': '#family #research', 'time': '2021-11-10, 00:38', 'due_date': '2021-11-03', 'id': 'hw0'}, {'content': 'sad', 'priority': 'Medium', 'tags': '#sda', 'time': '2021-11-10, 00:39', 'due_date': '2021-11-11', 'id': 'sad0'}]

def todolist_to_pd(to_do_list):
    '''takes in the to-do list dictionary from the main app file 
    and converts into pd'''
    df = pd.DataFrame.from_dict(to_do_list)
    df.drop("id", axis=1, inplace=True)

    df.columns = ["To-do", "Priority", "Tags", "Time Added", "Due Date"]
    return df

def to_gsheet(to_do_list):
    '''main function to output to google spreadsheet'''
    df = todolist_to_pd(to_do_list)

    # connect to google API and output
    sh = gc.open("CS321 project 3 To-do list")
    worksheet = sh[0]
    worksheet.clear()
    worksheet.set_dataframe(df, (1,1))


class KMeans():
    def __init__(self, data=None):
        '''KMeans constructor

        (Should not require any changes)

        Parameters:
        -----------
        data: ndarray. shape=(num_samps, num_features)
        '''

        # k: int. Number of clusters
        self.k = None
        # centroids: ndarray. shape=(k, self.num_features)
        #   k cluster centers
        self.centroids = None
        # data_centroid_labels: ndarray. shape=(self.num_samps,)
        #   Holds index of the assigned cluster of each data sample
        self.data_centroid_labels = None

        # inertia: float.
        #   Mean squared distance between each data sample and its assigned (nearest) centroid
        self.inertia = None

        # data: ndarray. shape=(num_samps, num_features)
        self.data = data
        # num_samps: int. Number of samples in the dataset
        self.num_samps = None
        # num_features: int. Number of features (variables) in the dataset
        self.num_features = None
        if data is not None:
            self.num_samps, self.num_features = data.shape

    def set_data(self, data):
        '''Replaces data instance variable with `data`.

        Reminder: Make sure to update the number of data samples and features!

        Parameters:
        -----------
        data: ndarray. shape=(num_samps, num_features)
        '''
        self.data = data
        self.num_samps = self.data.shape[0]
        self.num_features = self.data.shape[1]

    def get_data(self):
        '''Get a COPY of the data

        Returns:
        -----------
        ndarray. shape=(num_samps, num_features). COPY of the data
        '''
        return self.data.copy()

    def get_centroids(self):
        '''Get the K-means centroids

        (Should not require any changes)

        Returns:
        -----------
        ndarray. shape=(k, self.num_features).
        '''
        return self.centroids

    def get_data_centroid_labels(self):
        '''Get the data-to-cluster assignments

        (Should not require any changes)

        Returns:
        -----------
        ndarray. shape=(self.num_samps,)
        '''
        return self.data_centroid_labels

    def dist_pt_to_pt(self, pt_1, pt_2):
        '''Compute the Euclidean distance between data samples `pt_1` and `pt_2`

        Parameters:
        -----------
        pt_1: ndarray. shape=(num_features,)
        pt_2: ndarray. shape=(num_features,)

        Returns:
        -----------
        float. Euclidean distance between `pt_1` and `pt_2`.

        NOTE: Implement without any for loops (you will thank yourself later since you will wait
        only a small fraction of the time for your code to stop running)
        '''
        dist = np.square(pt_1 - pt_2)
        dist = np.sum(dist)
        dist = np.sqrt(dist)
        return dist

    def dist_pt_to_centroids(self, pt, centroids):
        '''Compute the Euclidean distance between data sample `pt` and and all the cluster centroids
        self.centroids

        Parameters:
        -----------
        pt: ndarray. shape=(num_features,)
        centroids: ndarray. shape=(C, num_features)
            C centroids, where C is an int.

        Returns:
        -----------
        ndarray. shape=(C,).
            distance between pt and each of the C centroids in `centroids`.

        NOTE: Implement without any for loops (you will thank yourself later since you will wait
        only a small fraction of the time for your code to stop running)
        '''
        dist = np.square(centroids - pt)
        dist = np.sum(dist, axis=1)
        dist = np.sqrt(dist)
        return dist

    def initialize(self, k):
        '''Initializes K-means by setting the initial centroids (means) to K unique randomly
        selected data samples

        Parameters:
        -----------
        k: int. Number of clusters

        Returns:
        -----------
        ndarray. shape=(k, self.num_features). Initial centroids for the k clusters.

        NOTE: Can be implemented without any for loops
        '''
        self.k = k
        random_idx = np.random.choice(self.num_samps, k, replace=False)

        centroids = self.data[np.ix_(random_idx, np.arange(self.num_features))]
        return centroids

    def initialize_plusplus(self, k):
        '''Initializes K-means by setting the initial centroids (means) according to the K-means++
        algorithm

        (LA section only)

        Parameters:
        -----------
        k: int. Number of clusters

        Returns:
        -----------
        ndarray. shape=(k, self.num_features). Initial centroids for the k clusters.

        TODO:
        - Set initial centroid (i = 0) to a random data sample.
        - To pick the i-th centroid (i > 0)
            - Compute the distance between all data samples and i-1 centroids already initialized.
            - Create the distance-based probability distribution (see notebook for equation).
            - Select the i-th centroid by randomly choosing a data sample according to the probability
            distribution.
        '''
        self.k = k
        centroids = np.zeros((k, self.num_features))
        
        index = np.random.choice(self.num_samps, 1, replace=False)
        centroids[0] = self.data[index]

        for i in range(1, self.k):
            sum_dist = np.zeros(self.num_samps)
            for samps in range(self.num_samps):
                min_dist = np.min(self.dist_pt_to_centroids(self.data[samps], centroids[:i]))
                sum_dist[samps] = min_dist

            prob = sum_dist/np.sum(sum_dist)
            index = np.random.choice(np.arange(self.num_samps), p=prob)
            centroids[i] = self.data[index]

        return centroids


    def cluster(self, k=2, tol=1e-5, max_iter=1000, init_method='random', verbose=False):
        '''Performs K-means clustering on the data

        Parameters:
        -----------
        k: int. Number of clusters
        tol: float. Terminate K-means if the difference between all the centroid values from the
        previous and current time step < `tol`.
        max_iter: int. Make sure that K-means does not run more than `max_iter` iterations.
        verbose: boolean. Print out debug information if set to True.

        Returns:
        -----------
        self.inertia. float. Mean squared distance between each data sample and its cluster mean
        int. Number of iterations that K-means was run for

        TODO:
        - Initialize K-means variables
        - Do K-means as long as the max number of iterations is not met AND the difference between
        the previous and current centroid values is > `tol`
        - Set instance variables based on computed values.
        (All instance variables defined in constructor should be populated with meaningful values)
        - Print out total number of iterations K-means ran for
        '''
        self.k = k
        count = 0

        if init_method == 'random':
            self.centroids = self.initialize(k)
        elif init_method == "kmeans++":
            self.centroids = self.initialize_plusplus(k)

        for i in range(max_iter):
            count += 1
            self.data_centroid_labels = self.update_labels(self.centroids)
            self.centroids, diff = self.update_centroids(self.k, self.data_centroid_labels, self.centroids)

            if np.all(np.absolute(diff) < tol):
                break

        self.inertia = self.compute_inertia()

        if verbose:
            print("total number of K-means iterations: ", count)
        
        return self.inertia, count

    def cluster_batch(self, k=2, n_iter=1, init_method='random', verbose=False):
        '''Run K-means multiple times, each time with different initial conditions.
        Keeps track of K-means instance that generates lowest inertia. Sets the following instance
        variables based on the best K-mean run:
        - self.centroids
        - self.data_centroid_labels
        - self.inertia

        Parameters:
        -----------
        k: int. Number of clusters
        n_iter: int. Number of times to run K-means with the designated `k` value.
        init_method: str. How to initialize the cluster centroids.
            'random': Pick random samples (without replacement)
            'kmeans++': Use K-means++ initialization
        verbose: boolean. Print out debug information if set to True.
        '''
        if n_iter < 1:
            return
        
        old_inertia, n = self.cluster(k, init_method=init_method, verbose=verbose)
        results = [self.centroids, self.data_centroid_labels, self.inertia]
        iters = np.zeros(n_iter)
        iters[0] = n

        for i in range (1, n_iter):
            new_inertia, n = self.cluster(k, init_method=init_method, verbose=verbose)
            iters[i] = n

            if new_inertia < old_inertia:
                results[0] = self.centroids
                results[1] = self.data_centroid_labels
                results[2] = self.inertia

        self.centroids, self.data_centroid_labels, self.inertia = results[0], results[1], results[2]
        return np.mean(iters)

    def update_labels(self, centroids):
        '''Assigns each data sample to the nearest centroid

        Parameters:
        -----------
        centroids: ndarray. shape=(k, self.num_features). Current centroids for the k clusters.

        Returns:
        -----------
        ndarray. shape=(self.num_samps,). Holds index of the assigned cluster of each data sample

        Example: If we have 3 clusters and we compute distances to data sample i: [0.1, 0.5, 0.05]
        labels[i] is 2. The entire labels array may look something like this: [0, 2, 1, 1, 0, ...]
        '''
        labels = []
        for i in range(self.num_samps):
            dist = self.dist_pt_to_centroids(self.data[i], centroids)
            index = np.argmin(dist)
            labels.append(index)

        return np.asarray(labels)

    def update_centroids(self, k, data_centroid_labels, prev_centroids):
        '''Computes each of the K centroids (means) based on the data assigned to each cluster

        Parameters:
        -----------
        k: int. Number of clusters
        data_centroid_labels. ndarray. shape=(self.num_samps,)
            Holds index of the assigned cluster of each data sample
        prev_centroids. ndarray. shape=(k, self.num_features)
            Holds centroids for each cluster computed on the PREVIOUS time step

        Returns:
        -----------
        new_centroids. ndarray. shape=(k, self.num_features).
            Centroids for each cluster computed on the CURRENT time step
        centroid_diff. ndarray. shape=(k, self.num_features).
            Difference between current and previous centroid values
        '''
        new_centroids = np.zeros([k, self.num_features])
        # print(data_centroid_labels)
        for i in range(k):
            new_centroids[i,:] = np.mean(self.data[data_centroid_labels == i,:], axis=0)
        centroid_diff = new_centroids - prev_centroids
        # print("previous centroids:\n", prev_centroids)
        # print("new:\n", new_centroids)
        # print("diff:\n", centroid_diff)
        return new_centroids, centroid_diff


    def compute_inertia(self):
        '''Mean squared distance between every data sample and its assigned (updatenearest) centroid

        Parameters:
        -----------
        None

        Returns:
        -----------
        float. The average squared distance between every data sample and its assigned cluster centroid.
        '''
        distance = np.zeros(self.num_samps)
        for i in range(self.num_samps):
            index = int(self.data_centroid_labels[i])
            dist = self.dist_pt_to_pt(self.data[i], self.centroids[index])
            distance[i] = np.square(dist)
        inertia = np.mean(distance)
        return inertia

    def plot_clusters(self):
        '''Creates a scatter plot of the data color-coded by cluster assignment.


        TODO:
        - Plot samples belonging to a cluster with the same color.
        - Plot the centroids in black with a different plot marker.
        - The default scatter plot color palette produces colors that may be difficult to discern
        (especially for those who are colorblind). Make sure you change your colors to be clearly
        differentiable.
            (LA Section): You should use a palette Colorbrewer2 palette. Pick one with a generous
            number of colors so that you don't run out if k is large (e.g. 10).
        '''
        plt.scatter(self.data[:,0], self.data[:,1], c=self.get_data_centroid_labels(), cmap = palettable.colorbrewer.diverging.Spectral_10.mpl_colormap)
        plt.scatter(self.centroids[:,0], self.centroids[:,1], c="black", marker="s")
        plt.xlabel("X")
        plt.ylabel("Y")

    def elbow_plot(self, max_k):
        '''Makes an elbow plot: cluster number (k) on x axis, inertia on y axis.

        Parameters:
        -----------
        max_k: int. Run k-means with k=1,2,...,max_k.

        TODO:
        - Run k-means with k=1,2,...,max_k, record the inertia.
        - Make the plot with appropriate x label, and y label, x tick marks.
        '''
        inertias = []
        for i in range(max_k):
            # inertias.append(self.cluster(i+1)[0])
            inertias.append(self.cluster(k=i+1)[0])

        plt.plot(np.arange(1, max_k+1), inertias)
        plt.xlabel("numer of clusters(k)")
        plt.ylabel("inertia")
        plt.xticks(np.arange(1, max_k))


    def replace_color_with_centroid(self):
        '''Replace each RGB pixel in self.data (flattened image) with the closest centroid value.
        Used with image compression after K-means is run on the image vector.

        Parameters:
        -----------
        None

        Returns:
        -----------
        None
        '''
        copy = self.data.copy()
        for i in range(self.num_samps):
            copy[i,:] = self.centroids[self.data_centroid_labels[i], :]
        self.data = copy


if __name__ == "__main__":
    to_gsheet(sample_list)
